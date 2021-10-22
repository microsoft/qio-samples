# Azure Quantum Optimization Sample: Secret Santa
# 
# This sample walks through how to solve the Secret Santa problem using Azure Quantum. The scenario is defined as follows:
# 
# - Vincent, Tess, and Uma each write their name on a slip of paper and place the paper in a jar.
# - Everybody then draws a slip of paper from the jar at random.
# - Each person buys a small gift and writes a poem for the person whose name they have drawn.
#   - If they draw their own name, they return the slip of paper and re-draw.
# 
# Note:
# The inspiration for this scenario came from Vincent's blog post (found here: https://vincent.frl/quantum-secret-santa/),
# which demonstrates how to use [Q# and the QDK](https://docs.microsoft.com/azure/quantum/overview-what-is-qsharp-and-qdk) to solve this scenario. In this sample, we will make use of the [Azure Quantum QIO service](https://docs.microsoft.com/azure/quantum/optimization-what-is-quantum-optimization) to solve the same problem.

# Import required modules
from typing import List
from azure.quantum import Workspace
from azure.quantum.optimization import Problem, ProblemType, Term, SimulatedAnnealing 

# Sign into your Azure Quantum workspace
# Copy the settings for your workspace below
workspace = Workspace(
    subscription_id = "",
    resource_group = "",
    name = "",
    location = ""
)

# Helper function to build terms with indices i, j:
def build_terms(i: int, j: int):
    """
    Construct Terms for a row or a column (two variables) of the Secret Santa matrix

    Arguments:
    i (int): index of first variable
    j (int): index of second variable

    """
    
    terms = []                                      # Initialize empty terms list
    terms.append(Term(c = 1.0, indices = [i, i]))   # x(i)^2
    terms.append(Term(c = 1.0, indices = [j, j]))   # x(j)^2
    terms.append(Term(c = 2.0, indices = [i, j]))   # 2x(i)x(j) 
    terms.append(Term(c = -2.0, indices = [i]))     # -2x(i)
    terms.append(Term(c = -2.0, indices = [j]))     # -2x(j)
    terms.append(Term(c = 1.0, indices = []))       # +1

    return terms

# Helper function to interpret the answer returned by the service in a human-readable way:
def print_results(config: dict) :
    """
    print results of run

    Arguements:
    config (dictionary): config returned from solver
    """
    result = {
                '0': 'Vincent buys Tess a gift and writes her a poem.',
                '1': 'Vincent buys Uma a gift and writes her a poem.',
                '2': 'Tess buys Vincent a gift and writes him a poem.',
                '3': 'Tess buys Uma a gift and writes her a poem.',
                '4': 'Uma buys Vincent a gift and writes him a poem.',
                '5': 'Uma buys Tess a gift and writes her a poem.'}

    for key, val in config.items():
        if val == 1:
            print(result[key])

# Bringing it all together:

"""
build secret santa matrix

        Vincent Tess Uma
Vincent    -    x(0) x(1)
Tess      x(2)   -   x(3)
Uma	      x(4)  x(5)  -
"""

#       row 0             + row 1             + row 2                
terms = build_terms(0, 1) + build_terms(2, 3) + build_terms(4, 5)

#             + col 0             + col 1             + col 2
terms = terms + build_terms(2, 4) + build_terms(0, 5) + build_terms(1, 3)

print(f'Terms: {terms}\n')

problem = Problem(name = 'secret santa', problem_type = ProblemType.pubo, terms = terms)

solver = SimulatedAnnealing(workspace, timeout = 2)

print('Submitting problem to Azure Quantum')
result = solver.optimize(problem)

print(f'\n\nResult: {result}\n')

print('Human-readable solution:')
print_results(result['configuration'])