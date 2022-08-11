#import dependencies 
import numpy as np
import math
from collections import defaultdict

from azure.identity import ClientSecretCredential
from azure.quantum import Workspace
from azure.quantum.optimization import Problem, ProblemType, Term
from azure.quantum.optimization import SimulatedAnnealing, ParallelTempering, Tabu, QuantumMonteCarlo, Solver


##### Fill in your workspace details to connect to the Azure QIO solvers.

workspace = Workspace (
    subscription_id = "",
    resource_group = "",
    name = "",
    location = ""
)

##### Some example sudokus that can be solved.

Sudoku4A = np.matrix([[0, 0, 1, 0],
                      [0, 0, 2, 0],
                      [0, 2, 0, 0],
                      [0, 4, 0, 0]
                    ])


Sudoku4B = np.matrix([[0, 0, 0, 0],
                      [1, 0, 3, 0],
                      [4, 3, 1, 0],
                      [2, 0, 0, 0]
                    ])


Sudoku9A = np.matrix([[1, 0, 0, 0, 5, 0, 0, 0, 3], 
                      [0, 0, 0, 0, 2, 1, 9, 0, 4],
                      [5, 9, 0, 0, 0, 6, 0, 0, 0],
                      [0, 3, 0, 0, 4, 0, 6, 1, 0],
                      [0, 0, 7, 0, 0, 3, 8, 0, 0],
                      [4, 0, 0, 1, 7, 0, 0, 0, 0],
                      [7, 0, 0, 9, 0, 5, 0, 3, 0],
                      [9, 8, 5, 0, 0, 0, 2, 0, 0],
                      [0, 0, 0, 0, 6, 0, 0, 0, 8]
                      ])


Sudoku9B = np.matrix([[0, 0, 0, 6, 0, 0, 4, 0, 5],
                      [0, 8, 6, 0, 0, 9, 0, 0, 0],
                      [0, 0, 0, 0, 0, 0, 8, 7, 0],
                      [6, 2, 0, 7, 0, 0, 3, 8, 0],
                      [0, 0, 0, 0, 0, 1, 0, 0, 9],
                      [5, 0, 3, 0, 0, 0, 0, 0, 4],
                      [0, 4, 7, 0, 9, 2, 0, 0, 0],
                      [0, 0, 0, 0, 0, 0, 0, 1, 2],
                      [8, 0, 0, 0, 3, 0, 5, 0, 0]
                     ])



def SudokuProblem(SudokuMatrix):

    terms = []
    N = len(SudokuMatrix)

    ####################################################################################################################################
    ##### Constraint 1: Per cell, only one variable may be '1', the others must be zero => then only one integer is assigned to the cell

    for row in range(0,N):                                     # iterate over the rows of the matrix
        for col in range(0,N):                                 # iterate over the columns of the matrix
            for ref in range(0,N):                           # select the reference variable in cell
                for tar in range(0,N):                       # select the target variable in cell  
                    if ref<tar:                              # prevent weighting combinations twice, therefore ref<tar
                        terms.append(
                            Term(
                                c = 1,
                                indices = [(pow(N,2)*row + N*col+ref),(pow(N,2)*row + N*col+tar)]   
                            )
                        )
                        ##### uncomment if you want to see the weighting combinations
                        # print(f'{(pow(N,2)*row + N*col+ref)},{(pow(N,2)*row + N*col+tar)}')  
    
    ####################################################################################################################################
    ##### Constraint 2: Per row, an integer may only appear once! 

    for row in range(0,N):                                   # iterate over the rows of the matrix                                     
        for ref in range(row*pow(N,2),(row+1)*pow(N,2)):     # select reference variable     
            for tar in range(ref,(row+1)*pow(N,2),N):        # select a target variable, which is the reference variable plus a multiple of N (same int but next cell)
                if ref<tar:                                  # prevent weighting combinations twice, therefore ref<tar
                    terms.append(
                        Term(
                            c = 1,
                            indices = [ref,tar]   
                        )
                    )
                    ##### uncomment if you want to see the weighting combinations
                    #print(f'{ref},{tar}')

    ####################################################################################################################################
    ##### Constraint 3: Per column, an integer may only appear once! 
    
    for ref in range(0,pow(N,3)):                            # select reference variable 
        for tar in range(ref,pow(N,3),pow(N,2)):             # select target variable, which is the reference variable plus a multiple of N^2 (same int but next row)
            if ref<tar:                                      # prevent weighting combinations twice, therefore ref<tar
                terms.append(
                    Term(
                        c = 1,
                        indices = [ref,tar]   
                    )
                )
                ##### uncomment if you want to see the weighting combinations
                #print(f'{ref},{tar}')

    ####################################################################################################################################
    ##### Constraint 4: In each box/area, an integer may only appear once! 

    ##### 1. First get the variables for each box (sub-matrix) and store it in a dictionary
    box_dict = defaultdict(dict)                                                                                        # define a dict for storing the variables per box
    for box_row in range(0,int(math.sqrt(N))):                                                                          # iterate over of row indices for the boxes
        for box_col in range(0,int(math.sqrt(N))):                                                                      # iterate over of column indices for the boxes
            box_dict[box_row][box_col] = []                                                                             # intialize list for a new box 
            for row_num in range(0,int(math.sqrt(N))):                                                                  # iterate over rows of a box (is multiplied by N^2 later)
                for row_i in range(0,int(N*math.sqrt(N))):                                                              # iterate over number of variables per row in a box                                                          
                    variable = int(row_i+(row_num*pow(N,2))+(box_row*pow(N,2)*math.sqrt(N)+box_col*N*math.sqrt(N)))     # compute variable number and append to list
                    box_dict[box_row][box_col].append(variable)                                                         # append variable list for that box inside a dict                     
                    ##### uncomment if you want to see the variables
                    #print(f'Added {variable} in list of box({box_row},{box_col})')

    ##### 2. Now weight the variables that represent the same value and are inside the same box 
    for box_row in range(0,int(math.sqrt(N))):                                                                          
        for box_col in range(0,int(math.sqrt(N))):
            box = box_dict[box_row][box_col]
            for shift in range(0,N):
                #print(f'shift:{shift}')
                for r in range(shift,len(box),N):
                    for t in range(r,len(box),N):
                        #print(r)
                        #print(t)

                        row_num_r = math.floor(box[r]/pow(N,2))
                        col_num_r = math.floor((box[r]%pow(N,2))/N)
                        row_num_t = math.floor(box[t]/pow(N,2))
                        col_num_t = math.floor((box[t]%pow(N,2))/N)

                        #print(f'ref:{row_num_r},{col_num_r}')
                        #print(f'tar:{row_num_t},{col_num_t}')
                        if row_num_r != row_num_t and col_num_r != col_num_t:
                            terms.append(
                                Term(
                                    c = 1,
                                    indices = [box[r],box[t]]   
                                )
                            )
                            #print(f'{box[r]},{box[t]}')                 

    ####################################################################################################################################
    ##### Constraint 5: Promote to fill in values - Values already in the sudoku get a higher weighting! 

    for row in range(0,N):
        for col in range(0,N):
            for val in range(1,N+1):
                if SudokuMatrix[row,col] == val:
                    terms.append(
                        Term(
                            c = -5,
                            indices = [(val-1)+col*N+row*pow(N,2)]   
                        )
                    )
                    #print('Directly influenced by initial conditions')
                    #print(f'{(val-1)+col*N+row*pow(N,2)}')
                elif SudokuMatrix[row,col] == 0:
                    terms.append(
                        Term(
                            c = -1,
                            indices = [(val-1)+col*N+row*pow(N,2)]   
                        )
                    )
                    #print('Not directly influenced by initial conditions')
                    #print(f'{(val-1)+col*N+row*pow(N,2)}') 

    return Problem(name="SudokuOptProblem", problem_type=ProblemType.pubo, terms=terms)

def ReadResults(Config: dict, SudokuMatrix):

    N = len(SudokuMatrix)

    #############################################################################################
    ##### Read the solver's solution (dictionary) and sort/order it 
    SortedAns = {}
    print('\n')
    SortedKeys = sorted({int(k):v for k,v in Config.items()}.keys())
    SortedAns = {k:Config[str(k)] for k in SortedKeys}
    #print(SortedAns)

    #############################################################################################
    ##### Iterate over solution and fill in the matrix
    SolvedSudoku = SudokuMatrix

    for k,v in SortedAns.items():
        if v==1:
            row_num = math.floor(k/pow(N,2))
            col_num = math.floor((k%pow(N,2))/N)                        
            val_num = math.floor(((k%pow(N,2))%N))+1
            SolvedSudoku[row_num,col_num] = val_num


    print(SolvedSudoku)

    InvalidSolution = VerifyResults(SortedAns, SolvedSudoku)


    return InvalidSolution



def VerifyResults(SortedAns, SolvedSudoku):

    N = len(SolvedSudoku)
    InvalidSolution = False

    ####################################################################################################################################
    ##### Check whether any cell has value 0
    for row in range(0,N):
        for col in range(0,N):
            if SolvedSudoku[row,col] == 0:
                #print('A zero was found - invalid')
                #print(f'{row},{col}')
                InvalidSolution = True

    ####################################################################################################################################
    ##### Check constraint 1: Per cell, only one variable may be '1', the others must be zero => then only one integer is assigned to the cell   
    for cell in range(0,pow(N,3),N):
        cell_sum = 0
        #print('\n')
        for i in range(0,N):
            #print(cell+i)
            cell_sum += SortedAns[cell+i]
        if cell_sum > 1:
            InvalidSolution = True
            print('More than one value per cell')
            print(SortedAns[cell+i])
            #raise RuntimeError(f'Too many cell values! {cell_sum} were specified for box ({math.floor((cell+i)/pow(N,2))},{math.floor(((cell+i)%pow(N,2))/N)})' )
        elif cell_sum == 0:
            print('Less than one value per cell')
            print(SortedAns[cell+i])
            InvalidSolution = True
            #raise RuntimeError(f'Too few cell values! {cell_sum} were specified for box ({math.floor((cell+i)/pow(N,2))},{math.floor(((cell+i)%pow(N,2))/N)})' )

    ####################################################################################################################################
    ##### Constraint 2: Per row, an integer may only appear once! 

    for i in range(0,N):
        for j in range(0,N):
            for k in range(0,N):
                if k>j:
                    if SolvedSudoku[i,k] == SolvedSudoku[i,j]:
                        #print(f'{i},{j},{k}')
                        print(f'Duplicate int in row {i+1}')
                        InvalidSolution = True

    ####################################################################################################################################
    ##### Constraint 2: Per column, an integer may only appear once! 

    for j in range(0,N):
        for i in range(0,N):
            for k in range(0,N):
                if k>i:
                    if SolvedSudoku[k,j] == SolvedSudoku[i,j]:
                        #print(f'{j},{i},{k}')
                        print(f'Duplicate int in column {j+1}')
                        InvalidSolution = True

    print(f"Is this solution valid? {not InvalidSolution}")

    return InvalidSolution


############################################################################################
##### Generate cost function
OptimizationProblem = SudokuProblem(Sudoku9B)

# Choose the solver and parameters --- uncomment if you wish to use a different one
solver = SimulatedAnnealing(workspace, timeout = 120)   
#solver = ParallelTempering(workspace, timeout = 120)
#solver = Tabu(workspace, timeout = 120)
#solver = QuantumMonteCarlo(workspace, sweeps = 2, trotter_number = 10, restarts = 72, seed = 22, beta_start = 0.1, transverse_field_start = 10, transverse_field_stop = 0.1) # QMC is not available parameter-free yet

SolverSolution = solver.optimize(OptimizationProblem)  
SolvedSudoku   = ReadResults(SolverSolution['configuration'], Sudoku9B)




