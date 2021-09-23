# # Squared-linear combination (SLC) terms used with the ship loading sample
# Ensure that you have the latest version of the Python SDK for Optimization installed. 
# You can use the commands below to update your SDK from inside the notebook. They are commented out so that they do not run each time you run the script.

## pip uninstall azure-quantum -y
## pip install azure-quantum

# Essential imports and workspace details.
# Please add your workspace details in the empty fields below.
# These can be retrieved via the command line if needed. Use 'az quantum workspace show'.

import time
from typing import List
from azure.quantum import Workspace
from azure.quantum.optimization import SubstochasticMonteCarlo
from azure.quantum.optimization import Problem, ProblemType, Term, SlcTerm, GroupType

workspace = Workspace (
  subscription_id = "",
  resource_group = "",
  name = "",
  location = ""
)

# Ship Loading Problem
# https://docs.microsoft.com/learn/modules/solve-quantum-inspired-optimization-problems/5-apply-quantum-inspired-optimization-real-world
# for details on the problem formulation - more context can also be found in the jupyter version of this sample

# define weights of the containers to be loaded

from azure.quantum.target.solvers import RangeSchedule
weights = [
    2, 5, 9, 21, 35, 5, 3, 5, 10, 11,
    23, 13, 8, 7, 12, 19, 22, 54, 33,
]

# Instantiate a solver
# Only Substochastic Monte Carlo and Population Annealing support squared linear terms at the time of writing

solver = SubstochasticMonteCarlo(
    workspace,
    step_limit=10000,
    target_population=64,
    beta=RangeSchedule("linear", 0.1, 5),
    seed=42
)

# Create the expanded cost function (same as in the base sample) where we use monomial terms only

def createFBP_expanded(weights: List[int]) -> Problem:
    # Expand the squared summation
    terms = []
    for i in range(len(weights)):
        for j in range(i+1, len(weights)):
            terms.append(
                Term(
                    c = 2 * weights[i] * weights[j],
                    indices = [i, j]
                )
            )

    # Return an Ising-type problem
    return Problem(name="Freight Balancing Problem", problem_type=ProblemType.ising, terms=terms)

problem_expanded = createFBP_expanded(weights)

# Create the factored cost function (using slc terms) 
# This allows us to compare the efficiency of the two approaches

def createFBP_factored(weights: List[int]) -> Problem:
    # Construct the factored form
    terms = [
        SlcTerm(
            c = 1,
            terms = [
                Term(
                    c = weights[i],
                    indices = [i]
                )
            for i in range(len(weights))]
        )
    ]
    
    # Return an Ising-type problem
    return Problem(name="Freight Balancing Problem", problem_type=ProblemType.ising, terms=terms)

# Create expanded problem for the given list of weights:
problem_factored = createFBP_factored(weights)

# Run the optimization for both formulations

# Optimize the expanded problem
print('Submitting expanded problem...')
start = time.time()
result = solver.optimize(problem_expanded)

# print time so that we can compare
timeElapsed = time.time() - start
print('Result in {:.1f} seconds: '.format(timeElapsed), result)

# To compare the accuracy/cost, we must add in the constant value from the factored terms
constant_cost = 0
for w in weights:
    constant_cost += w**2
print('constant cost: ', constant_cost)

# Optimize the factored problem
print('Submitting factored problem...')
start = time.time()
result = solver.optimize(problem_factored)

# print time so that we can compare
timeElapsed = time.time() - start
print('Result in {:.1f} seconds: '.format(timeElapsed), result)
