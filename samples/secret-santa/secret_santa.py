from typing import List

from azure.quantum import Workspace
from azure.quantum.optimization import Problem, ProblemType, Term, ParallelTempering, SimulatedAnnealing

# Workspace information
workspace = Workspace(
    subscription_id =   'xxx', # add your subscription_id
    resource_group =    'xxx', # add your resource_group
    name =              'xxx', # add your workspace name
)

print ( 'init...' )

# login
workspace.login() #refresh=True
print ( 'login successful' )

def build_terms ( i : int , j : int ) :
    """
    Construct Terms for a row or a column ( two variables ) of the secret santa matrix

    for x(i) XOR x(j) minimize:  ( x(i) + x(j) - 1 )**2

    expanded:  x(i)**2 + x(j)**2 + 2x(i)x(j) - 2x(i) - 2x(j) + 1

    Arguments:
    i (int): index of first variable
    j (int): index of second variable

    """
    
    terms = [ Term ( c = 1.0 , indices = [ i , i ] ) ]        # x(i)**2
    terms.append ( Term ( c = 1.0 , indices = [ j , j ] ) )   # x(j)**2
    terms.append ( Term ( c = 2.0 , indices = [ i , j ] ) )   # 2x(i)x(j) 
    terms.append ( Term ( c = -2.0 , indices = [ i ] ) )      # -2x(i)
    terms.append ( Term ( c = -2.0 , indices = [ j ] ) )      # -2x(j)
    terms.append ( Term ( c = 1.0 , indices = [] ) )          # +1

    return terms

def print_results ( config : dict ) :
    """
    print results of run

    Arguements:
    config (dictionary): config returned from solver
    """
    result =  { '0' : 'Vincent buys Tess a gift and writes her a poem' ,
                '1' : 'Vincent buys Uma a gift and writes her a poem' ,
                '2' : 'Tess buys Vincent a gift and writes him a poem' ,
                '3' : 'Tess buys Uma a gift and writes her a poem' ,
                '4' : 'Uma buys Vincent a gift and writes him a poem' ,
                '5' : 'Uma buys Tess a gift and writes her a poem' }

    for key, val in config.items() :
        if val == 1 :
            print ( result [ key ] )

"""
build secret santa matrix

	    Vincent Tess Uma
Vincent    -    x(0) x(1)
Tess      x(2)   -   x(3)
Uma	      x(4)  x(5)  -

"""

#terms = build_terms ( 2 , 4 ) + build_terms ( 2 , 3 ) + build_terms ( 4 , 5 ) + build_terms ( 1 , 3 ) + build_terms ( 0 , 5 ) + build_terms ( 0 , 1 )

#       row 0                 + row 1                 + row 2                 + col 0                 + col 1                 + col 2
terms = build_terms ( 0 , 1 ) + build_terms ( 2 , 3 ) + build_terms ( 4 , 5 ) + build_terms ( 2 , 4 ) + build_terms ( 0 , 5 ) + build_terms ( 1 , 3 )


print ( 'terms' )
print ( terms )
print ( ' ' )

problem = Problem ( name = 'secret santa' , problem_type = ProblemType.pubo , terms = terms )

solver = SimulatedAnnealing ( workspace , timeout = 100 )

print ( 'calling solver' )
result = solver.optimize ( problem )

print_results ( result [ "configuration" ] )

print ( '...fini' )
