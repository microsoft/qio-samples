import time
from math import log2, floor
from azure.quantum import Workspace
from azure.quantum.optimization import Problem, ProblemType, Term, ParallelTempering, Tabu, SimulatedAnnealing
from azure.identity import ClientSecretCredential
from mpl_toolkits import mplot3d
import numpy as np
import matplotlib.pyplot as plt


workspace = Workspace(
  subscription_id   = ,
  resource_group    = ,
  name              = ,
  location          = ,
  credential        = ClientSecretCredential(tenant_id=,
                                            client_id=,
                                            client_secret=)
)

def direction_variables(direction: str, offset: int, sign_dir: int, sign_pos: int, lambda_: int) -> list:

    '''
    Purpose:
        Translates the direction (+x,-x,+y,-y,+z,-z) of turn 'i' as a function of three q's. (Three optimization variables because of the defined coordinate system).
    Example:
        Direction "+z" in the first turn (turn = 1) is translated to: q_{0+offset}q_{2+offset}-q_{0+offset}q_{1+offset}q_{2+offset}.
    Inputs:
        1. direction: A direction from an x-y-z coordinate system, one of the following: ('+x','-x','+y','-y','+z','-z').
        2. offset:    Offset gives the turn number expressed in the first q of that turn. 
            Example: Turn 1 starts with q_0, offset=0. Turn 2 starts with q_3, offset = 3.
        3. sign_dir:  Changes the sign of the weights corresponding to negative directions "-x", "-y", "-z" -> necessary for finding the positions, for exmaple (+x) "-" (-x).
        4. sign_pos:  Changes the sign of the weights corresponding to negative positions  "-(x,y,z)"      -> necessary for finding the distances between node "i" and node "j".
        5. lambda_:   The weight term associated with a constraint.
    Output:
        1. A list of term objects.
    '''

    terms = []
    if direction == "+x":
        term_0 = Term(c= 1*sign_pos*lambda_,  indices=[0+offset])
        term_1 = Term(c=-1*sign_pos*lambda_,  indices=[0+offset, 1+offset])
        term_2 = Term(c=-1*sign_pos*lambda_,  indices=[0+offset, 2+offset])
        term_3 = Term(c= 1*sign_pos*lambda_,  indices=[0+offset, 1+offset, 2+offset])
        terms  = [term_0, term_1, term_2, term_3]
    elif direction == "-x":
        term_0 = Term(c= 1*sign_dir*sign_pos*lambda_,  indices=[1+offset])
        term_1 = Term(c=-1*sign_dir*sign_pos*lambda_,  indices=[0+offset, 1+offset])
        term_2 = Term(c=-1*sign_dir*sign_pos*lambda_,  indices=[1+offset, 2+offset])
        term_3 = Term(c= 1*sign_dir*sign_pos*lambda_,  indices=[0+offset, 1+offset, 2+offset])
        terms  = [term_0, term_1, term_2, term_3]
    elif direction == "+y":
        term_0 = Term(c= 1*sign_pos*lambda_,  indices=[2+offset])
        term_1 = Term(c=-1*sign_pos*lambda_,  indices=[0+offset, 2+offset])
        term_2 = Term(c=-1*sign_pos*lambda_,  indices=[1+offset, 2+offset])
        term_3 = Term(c= 1*sign_pos*lambda_,  indices=[0+offset, 1+offset, 2+offset])
        terms  = [term_0, term_1, term_2, term_3]
    elif direction == "-y":
        term_0 = Term(c= 1*sign_dir*sign_pos*lambda_,  indices=[0+offset, 1+offset])
        term_1 = Term(c=-1*sign_dir*sign_pos*lambda_,  indices=[0+offset, 1+offset, 2+offset])
        terms  = [term_0, term_1]
    elif direction == "+z":
        term_0 = Term(c= 1*sign_pos*lambda_,  indices=[0+offset, 2+offset])
        term_1 = Term(c=-1*sign_pos*lambda_,  indices=[0+offset, 1+offset, 2+offset])
        terms  = [term_0, term_1]
    elif direction == "-z":
        term_0 = Term(c= 1*sign_dir*sign_pos*lambda_,  indices=[1+offset, 2+offset])
        term_1 = Term(c=-1*sign_dir*sign_pos*lambda_,  indices=[0+offset, 1+offset, 2+offset])
        terms  = [term_0, term_1]
    return terms

def print_cost_function(terms: list):

    '''
    Purpose:
        Takes a list of terms and prints it out as a (mathematical) cost function.
    Example:
        {'c': 1, 'ids': [0, 10, 11, 12]}  ---> 1q_0q_10q_11q_12
    Inputs:
        1. terms: the list of terms.
    '''

    final_string = ''
    final_string = ''
    for term in terms:
        term = term.to_dict()
        weight = term['c']
        ids    = term['ids']
        string = '('
        if weight >= 0:
            string = '+' + '('+str(weight)
        if weight < 0:
            string = '-' + '(' + str(abs(weight))
        for id_ in ids:
            string = string + f'q_{id_}'
        string = string + ')'
        final_string = final_string + string
    print('[' + final_string + ']')


def generate_slack_coefficients(turn_diff: int):

    ''' 
    Purpose: 
        Calculates the number of slack variables and their weights.
    Example:
        For the constraint: x1 + x2 + x3 + x4 <= 4 which is converted to x1 + x2 + x3 + x4 + s1 + s2 +2*s3 = 4, 
        with 's' being slack variables. This function computes the weights of these slack variables ([1,1,2] for the example).
    Input:
        1. turn_diff: the differences in turns (end_turn - start_turn).
    Output:
        1. y: the weights of the slack variables.
    '''

    dist_diff = (turn_diff**2)-1
    if dist_diff == 0:
        y = []
    elif dist_diff > 0:
        M = floor(log2(dist_diff))
        y = [2**n for n in range(M)]
        y.append(dist_diff + 1 - 2**M)
    return y


def simplify_every_iter_function(term_list: list[Term], ref_term:Term) -> list[Term]:
    terms = []
    same_ids_list = []
    diff_ids_list = []
    if term_list:
        for term_in_list in term_list:
            if sorted(ref_term.ids) == sorted(term_in_list.ids):
                same_ids_list += [term_in_list] 
            else: 
                diff_ids_list += [term_in_list]  
    if same_ids_list:
        new_weight = ref_term.c
        ids        = sorted(ref_term.ids)
        for same_ids_term in same_ids_list:
            new_weight += same_ids_term.c
        terms += [Term(c=new_weight, indices=ids)]    
    else:
        terms += [ref_term]
    if diff_ids_list:
        terms += diff_ids_list
    return terms


def diff_in_pos(start_turn: int, end_turn: int, num_dim: int, lamda_: int):

    '''
    Purpose:
        Expresses the difference in position (x,y,z) between two turns as a function of the encoding of the directions.
        In other words, expresses the difference in the position after the start_turn and position after the end_turn.
    Example:
        Difference between turn 0 (no turns yet, initial position = (0,0,0)) and turn 2:
            x(2) = [ move(+x, turn 1) - move(-x, turn 1) ] + [ move(+x, turn 2) - move(-x, turn 2) ]
            Note: only one 'move' per turn gets activated as they are represented by the same q's (ex. turn 1 is represented by q_0, q_1, and q_2).
    Inputs:
        1. start_turn:  the initial (reference) turn.
        2. end_turn:    the final (target) turn.
        3. num_dim:     the number of dimensions (3, x-y-z coordinate system).
    Outputs:
        1. The difference in the x direction.
        2. The difference in the y direction.
        3. The difference in the z direction. 
    '''

    x_diff = y_diff = z_diff = []
    if start_turn < end_turn and start_turn >= 0 and end_turn >= 1:
        for turn in range(start_turn,end_turn+1):
            x_diff += direction_variables("+x",(turn-1)*num_dim,1,1,lamda_)+direction_variables("-x",(turn-1)*num_dim,-1,1,lamda_)
            y_diff += direction_variables("+y",(turn-1)*num_dim,1,1,lamda_)+direction_variables("-y",(turn-1)*num_dim,-1,1,lamda_)
            z_diff += direction_variables("+z",(turn-1)*num_dim,1,1,lamda_)+direction_variables("-z",(turn-1)*num_dim,-1,1,lamda_)
    return x_diff, y_diff, z_diff

def cross_multiply(list_a: list[Term], list_b: list[Term]) -> list:

    '''
    Purpose: Cross multiplies two lists of terms (linear ex. [q_0 + q_1] or non-linear ex. [q_0q_1]) to return the expansion.
             Can compute powers of groups this way (^2, ^3,...), like squaring a list of terms.
             Calculates the expansion locally, unlike the SlcTerm class.
    Example: (2q_0q_1+3q_2q_3)^2 => (2q_0q_1)^2 + 12q_0q_1q_2q_3 + (3q_2q_3)^2
    Input:
        1. list_a: list which serves as the reference list (first 'for' loop).
        2. list_b: list which serves as the target list (second 'for' loop).
    Output:
        1. list of term objects.
    '''

    terms = []
    for one in list_a:
        for uno in list_b:
            weight = one.c * uno.c
            ids    = one.ids + uno.ids
            new_term = Term(c = weight, indices = ids)
            terms   += [new_term]
            #terms   = simplify_function(terms, new_term)
    return terms

def distance_constraint(num_turns: int, num_dim: int, lambda_0: int) -> list:

    '''
    Purpose:
        Build the distance contraint based on previosly defined functions.
        Constraint: Distance squared between i and j must be larger or equal to 1.
        Constraint: L_{i,j}^2 >= 1  => L_{i,j}^2 = 1+q_{slacker}   (converting the inequality constraint to an equality constraint.)
    Example/Explanation:
        L{1,2}^2 = (x1-x2)^2 + (y1-y2)^2 + (z1-z2)^2
        x1 = [move(+x1)-move(-x1)]
        x2 = [move(+x1)-move(-x1)] + [move(+x2)-move(-x2)]
        < same for other dimensions >
        < fill into first line >
        L{1,2}^2 = [move(+x2)-move(-x2)]^2 + [move(+y2)-move(-y2)]^2 + [move(+z2)-move(-z2)]^2
        [move(+x2)-move(-x2)]^2 + [move(+y2)-move(-y2)]^2 + [move(+z2)-move(-z2)]^2 - q_{slacker} = 0  ---> expressed in q's == cost function
    Inputs:
        1. num_turns: the number of turns.
        2. num_dum: the number of dimensions.
        3. lambda_0: the constraint weight for the distance constraint.
    Output:
        1. List of term objects describing the distance constraint.
    '''

    terms = []
    slack_indexer = 0
    for start_turn in range(1,num_turns+1):
        for end_turn in range(start_turn+1,num_turns+2):
            # Calculate the differences in positions for each dimension. 
            x_diff_i_j,     y_diff_i_j,     z_diff_i_j      = diff_in_pos(start_turn, end_turn, num_dim, lambda_0)
            # Compute the squared distance (Pythagorean theorem) by calculating the squared expansion.
            x_diff_i_j_2,   y_diff_i_j_2,   z_diff_i_j_2    = cross_multiply(x_diff_i_j,x_diff_i_j), cross_multiply(y_diff_i_j,y_diff_i_j), cross_multiply(z_diff_i_j,z_diff_i_j)  
            # Add slack variables due to inequality constraint.      
            slack_var_terms = []
            slack_coefficients = generate_slack_coefficients(end_turn-start_turn)
            for s in range(0,len(slack_coefficients)):
                slack_var_terms += [Term(c=-slack_coefficients[s], indices=[num_turns*num_dim+slack_indexer+s])]

            terms += x_diff_i_j_2 + y_diff_i_j_2 + z_diff_i_j_2 + slack_var_terms
            slack_indexer+=len(slack_coefficients)
    return terms

def penalize_000(len_seq: int, num_dim: int, lambda_2: int) -> list:

    '''
    Purpose:
        Build the constraint that penalizes the invalid moves associated with the substring: '000'.
        The constraint needs to be defined over the set of all turns, as defined by the 'for' loop.
    Example:
        If turn 2 (q_3q_4q_5) equals '000', assign a large penalty.
    Inputs:
        1. len_seq:   the number nodes to consider.
        2. num_dim:   the number of dimensions (which is 3).
        3. lambda_2:  the penalty weight for this constraint.
    Outputs:
        1. List of term objects.
    '''
  
    terms = []
    for k in range(0,len_seq):
        offset = k*num_dim
        term_0 = Term(c=-1*lambda_2,indices=[0+offset])
        term_1 = Term(c=-1*lambda_2,indices=[1+offset])
        term_2 = Term(c=-1*lambda_2,indices=[2+offset])
        term_3 = Term(c= 1*lambda_2,indices=[0+offset,1+offset])
        term_4 = Term(c= 1*lambda_2,indices=[0+offset,2+offset])
        term_5 = Term(c= 1*lambda_2,indices=[1+offset,2+offset])
        term_6 = Term(c=-1*lambda_2,indices=[0+offset,1+offset,2+offset])
        terms  += [term_0, term_1, term_2, term_3, term_4, term_5, term_6]
    return terms

def penalize_111(len_seq: int, num_dim: int, lambda_3: int) -> list:

    '''
    Purpose:
        Build the constraint that penalizes the invalid moves associated with the  substring: '111'.
        The constraint needs to be defined over the set of all turns, as defined by the 'for' loop.
    Example:
        If turn 2 (q_3q_4q_5) equals '111', assign a large penalty.
    Inputs:
        1. len_seq:   the number nodes to consider.
        2. num_dim:   the number of dimensions (which is 3 in this sample).
        3. lambda_3:  the penalty weight for this constraint.
    Outputs:
        1. List of term objects.
    '''

    terms = []
    for k in range(0,len_seq):
        offset = k*num_dim      
        terms += [Term(c=1*lambda_3,indices=[0+offset,1+offset,2+offset])]
    return terms

def no_return_constraint(num_turns: int, num_dim: int, lamda_4: int)-> list:
    
    '''
    Purpose:
        Build the constraint that penalizes going back to the same position/node two turns later.
    Example:
        Node A ---> <move +x> ---> Node B ---> <move -x> ---> Node A  => erroneous as we've been there already.
        Two sequential moves may not be in the same dimension and in opposite directions:  (+x then -x), (-x then +x), (+y then -y) etc.
    Inputs:
        1. num_turns: the number of turns.
        2. num_dim  : the number of dimensions, which is 3 for this sample.
        3. lambda_4 : the penalty weight for this constraint.
    Outputs:
        1. List of term objects.
    '''

    terms = []
    for i in range(0,num_turns):
        x_out_in     = cross_multiply(direction_variables("+x",i*num_dim,1,1,lamda_4), direction_variables("-x",(i+1)*num_dim,1,1,lamda_4))
        x_in_out     = cross_multiply(direction_variables("-x",i*num_dim,1,1,lamda_4), direction_variables("+x",(i+1)*num_dim,1,1,lamda_4))
        y_right_left = cross_multiply(direction_variables("+y",i*num_dim,1,1,lamda_4), direction_variables("-y",(i+1)*num_dim,1,1,lamda_4))
        y_left_right = cross_multiply(direction_variables("-y",i*num_dim,1,1,lamda_4), direction_variables("+y",(i+1)*num_dim,1,1,lamda_4))
        z_up_down    = cross_multiply(direction_variables("+z",i*num_dim,1,1,lamda_4), direction_variables("-z",(i+1)*num_dim,1,1,lamda_4))
        z_down_up    = cross_multiply(direction_variables("-z",i*num_dim,1,1,lamda_4), direction_variables("+z",(i+1)*num_dim,1,1,lamda_4))
        terms += x_out_in + x_in_out + y_right_left + y_left_right + z_up_down + z_down_up
    return terms
    


def read_validate_solution(solution: dict, num_turns: int, num_dim: int):
    
    '''
    Purpose:
        To validate the solution returned by the solver. Make it readable, and analyze if it makes sense.
    Inputs:
        1. solution:   The solution results dictionary which is returned by the solver (results["configuration"]).
        2. num_turns:  The number of turns for the simulation.
        3. num_dim:    The number of dimensions, which is 3 for this sample (3D).
    Outputs:
        1. valid:      A boolean variable that specifies the validity of the solution.
        2. pos_dit:    Layered position dictionary that contains all of the nodes' locations per turn {turn: {x: x_pos, y:y_pos, z:z_pos}}.
        3. dir_dict:   Dictionary containing the linguistic interpretation of the 3-substring directions.
        4. var_dict:   Dictionary containing the spin per optimized variable
        5. x_arr:      Array of x positions.
        6. y_arr:      Array of y positions.
        7. z_arr:      Array of z positions. 
    '''

    print('\n')
    valid       = True
    move        = ''
    sol_str     = ''
    x_arr       = [0]
    y_arr       = [0]
    z_arr       = [0]
    dir_dict    = {'100':'out','010':'in','001':'right','110':'left','101':'up','011':'down'}
    pos_dict    = {0:{"x":0, "y":0, "z":0}}
    var_dict  = {}
    for key,val in solution:
        if key<(num_turns*num_dim):
            turn = floor(key/num_dim)+1
            print("Turn: "+str(turn),"var: "+str(key),"spin: "+str(val))
            var_dict |= {str(key): val}
        if key%3<num_dim and key<(num_turns*num_dim):
            move = move+str(val)
            if move in dir_dict:
                x_pos = pos_dict[turn-1]["x"]
                y_pos = pos_dict[turn-1]["y"]
                z_pos = pos_dict[turn-1]["z"]
                if dir_dict[move] == "out":
                    x_pos +=  1
                elif dir_dict[move] == "in":
                    x_pos += -1
                elif dir_dict[move] == "right":
                    y_pos +=  1
                elif dir_dict[move] == "left":
                    y_pos += -1
                elif dir_dict[move] == "up":
                    z_pos +=  1
                elif dir_dict[move] == "down":
                    z_pos += -1
                new_pos = {turn: {"x":x_pos, "y":y_pos, "z":z_pos}}
                pos_dict |= new_pos
                x_arr += [x_pos]
                y_arr += [y_pos]
                z_arr += [z_pos]
                #print move
                print(dir_dict[move], '\n')
                sol_str = sol_str + " "+ dir_dict[move]
                move = ''

            elif move == ('111' or '000'):
                valid = False
                print('Illegal move')
            
    print("solution:", sol_str, '\n')
    print("positions: ", pos_dict)

    incorrect_pos = []
    for ref in range(0,len(pos_dict)):
        for tar in range(ref+1,len(pos_dict)):
            if pos_dict[ref] == pos_dict[tar]:
                print(f"Invalid position. Position already taken. Positions {ref}-{tar}, (if difference = 2, increase lambda_4, otherwise increase lambda_1)") 
                valid = False
                incorrect_pos += [ref,tar]

    print('\n Incorrect positions',incorrect_pos)
    return valid, pos_dict, dir_dict, var_dict, x_arr, y_arr, z_arr

def submit():

    '''
    Purpose:
        This function submits to the Azure solvers.
        Adjust the variables and solver properties here.
        This functions coordinates the entire simulation by calling the previously defined functions.
    '''

    #simulated annealing
    nodes               = "HHHHHHHH"                                 # The 15 nodes that will be analyzed. 
    len_seq             = len(nodes)                                        # The length of the sequence.
    num_turns           = len(nodes)-1                                      # The number of turns (interconnection between nodes). There are N-1 turns.
    num_dim             = 3                                                 # Number of optimization variables required to describe a turn
    lambda_0            = 1
    lambda_2            = 100
    lambda_3            = 100
    lambda_4            = 1

    terms = ( distance_constraint(num_turns, num_dim, lambda_0)+penalize_000(len_seq, num_dim, lambda_2)+ 
              penalize_111(len_seq, num_dim, lambda_3)+no_return_constraint(num_turns, num_dim, lambda_4) )

    problem = Problem(name="Self Avoiding Walk Problem", problem_type=ProblemType.pubo, terms=terms)

    # Submit
    start = time.time()

    # Play with the timeouts
    solver = SimulatedAnnealing(workspace, timeout = 3600)
    #solver = ParallelTempering(workspace, timeout = 3600)
    #solver = Tabu(workspace, timeout = 3600)

    # Tuned (parameterized) simulated annealing solver. 
    #solver = SimulatedAnnealing(workspace, sweeps=50, restarts=2000, beta_start=1e-8, beta_stop=10, timeout=3600)
    
    print('Submitting problem...')
    job = solver.submit(problem)

    while job.details.status != 'Succeeded' and job.details.status != 'Failed':
        job.refresh()
        print('waiting')
        time.sleep(3)

    # Results
    results = job.get_results()
    print('\n Results:', results)
    config  = results["configuration"]
    
    time_elapsed = time.time() - start
    print("Execution time in seconds: ", time_elapsed, '\n')
    
    solution = [(int(k),v) for k, v in config.items()]
    solution.sort(key=lambda tup: tup[0])

    valid, posDict, dirDict, configDict, x_arr, y_arr, z_arr = read_validate_solution(solution, num_turns, num_dim)

    plot_path(x_arr, y_arr, z_arr)

def plot_path(x_arr,y_arr,z_arr):
    
    '''
    Purpose:
        This function plots the path of the self-avoiding walk through the position arrays.
    Inputs: 
        1. x_arr: the array of x positions.
        2. y_arr: the array of y positions.
        3. z_arr: the array of z positions.
    Outputs:
        1. The 3D plot of the self-avoiding path.
    '''
    print('\n')
    print('x_arr: ', x_arr)
    print('y_arr: ', y_arr)
    print('z_arr: ', z_arr)
    
    fig = plt.figure()
    ax = plt.axes(projection ='3d')
    # plotting
    ax.plot3D(x_arr, y_arr, z_arr, 'g-o')
    ax.set_title('3D self-avoiding path')
    plt.plot(0,0,0,'r+') # plot initial position
    plt.show()

submit()

