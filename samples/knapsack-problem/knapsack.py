
#!/usr/bin/env python
# coding: utf-8

# Knapsack sample
## The knapsack problem is a common approach in solving optimization problems in many industries.

# Representation of the Hamiltonian is PUBO in this implementation.
# The implementation is based on Andrew Lucas, Lyman Laboratory of Physics, Department of Physics, Harvard University, Cambridge, MA, USA,
# "Ising formulations of many NP problems"
# https://internal-journal.frontiersin.org/articles/10.3389/fphy.2014.00005/full

from azure.quantum.optimization import Term
from math import floor, log2
# This allows you to connect to the Workspace you've previously deployed in Azure.
# Be sure to fill in the settings below which can be retrieved by running 'az quantum workspace show' in the terminal.
from azure.quantum import Workspace

# Copy the settings for your workspace below
workspace = Workspace (
  subscription_id = "",
  resource_group = "",
  name = "",
  location = ""
)

# costsArray: the costs of the items represented as an array
# weightsArray: the weights of the items represented as an array
# W: the size of our knapsack
def knapsackHamiltonian(costsArray, weightsArray, W):
    
    terms = []

    maxCosts = max(costsArray)

    n = len(costsArray)


    # define auxiliary variables as suggested in Lucas paper
    # W=(W+1-2^M)_yM + sum from i=0 to M-1 of (2^i y_i)
    # it's important to understand that (W+1-2^M)_yM represents the last step.

    # M is log_2 W
    M = floor(log2(W))
    # k is the formular to encode W by auxiliary variables y
    # y_i is defined as y_0 to y_M
    k = [2**i for i in range(M)]
    # the mentioned last step
    k.append(W + 1 - 2**M)
    
    # x-Term
    for i in range(n):
        terms.append(Term(c=float(maxCosts * (weightsArray[i]**2) - costsArray[i]), indices=[i]))

    # x-x Term
    for i in range(n):
        for j in range(i+1, n):
            terms.append(Term(c=float(2*maxCosts*weightsArray[i]*weightsArray[j]), indices=[i,j]))

    # x-y Term
    for i in range(n):
        for j in range(M+1):
            terms.append(Term(c=float(-2*maxCosts*weightsArray[i]*k[j]), indices=[i,(n-1)+j]))

    # y Term
    for i in range(M+1):
        terms.append(Term(c=float(maxCosts*(k[i]**2)), indices=[(n-1)+i]))
        

    # y-y Term
    for i in range(M+1):
        for j in range(i+1, M+1):
            terms.append(Term(c=float(2*maxCosts*k[i]*k[j]), indices=[(n-1)+i,(n-1)+j]))

    return terms

from azure.quantum.optimization import Problem, ProblemType
from azure.quantum.optimization import SimulatedAnnealing # Change this line to match the Azure Quantum Optimization solver type you wish to use
# run the optimization

# sample data
costsArray = [5, 4, 2, 1, 4]
weightsArray = [7, 2, 5, 6, 8]
Weight = 15

terms = knapsackHamiltonian(costsArray, weightsArray, Weight)
problem = Problem(name="knapsack problem", problem_type=ProblemType.pubo, terms=terms)
solver = SimulatedAnnealing(workspace, timeout=100, seed=22)

job = solver.submit(problem)
job.refresh()
result = job.get_results()
config = result['configuration']
resultitems = []
for i in config.keys():
    if config[i]:
         resultitems.append(int(i))
    
for i in resultitems:
    if i < len(costsArray):
        print("Picked item number " + str(i))
