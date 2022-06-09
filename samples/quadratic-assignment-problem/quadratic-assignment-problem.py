#!/usr/bin/env python
# coding: utf-8

# # Quadratic Assignment Problem Sample
# 
# **Workspace Setup**  
# An Azure Quantum workspace is needed for this sample. You will need to enter your Azure Quantum workspace details in the cell below before you submit a problem:

# You may need to upgrade your SDK to a version that supports SlcTerm
# pip install azure-quantum --upgrade

import time
from typing import List
from azure.quantum import Workspace
from azure.quantum.optimization import PopulationAnnealing
from azure.quantum.optimization import Problem, ProblemType, Term, SlcTerm, GroupType

# This allows you to connect to the Workspace you've previously deployed in Azure.
# Be sure to fill in the settings below which can be retrieved by running 'az quantum workspace show' in the terminal.
workspace = Workspace (
  subscription_id = "",
  resource_group = "",
  name = "",
  location = ""
)

# Quadratic Assignment Problem
# The problem definition consists of 2 adjacency matrices representing the costs between different locations and different facilities.
locations = [
    [0, 2, 20],
    [2, 0, 14],
    [20, 14,0]
]

facilities = [
    [0, 100, 0],
    [100, 0, 5],
    [0, 5, 0]
]

# Mapping variable ids
# We will assign a numerical id to each x_i,j variable for a total of 9 variables
# Here, n is the number of locations/facilities
n = 3
variable_map = {}
for i in range(n):
    for j in range(n):
        variable_map[(i,j)] = i*n + j

# We will construct the problem terms and store them in this list.
terms_list = [] 

# Iterate through each variable and build its neighbours. For simplicity, we will not merge common terms.
for x1 in variable_map: 
    i,j = x1
    
    # neighbours are other variables that do not share the same location/facility as the current one
    neighbours = [var for var in variable_map if var[0] != i and var[1] != j]
    for x2 in neighbours:
        i2,j2 = x2
        c = locations[j][j2]*facilities[i][i2]/2.0 # divide by 2 because of symmetrical matrix
        terms_list.append(Term(c=c, indices=[variable_map[x1], variable_map[x2]]))

print("variables -> ids:", variable_map)
print("\nterms:", terms_list)


# Constraints and Penalty Terms
# We set penalty to the largest coefficient in the original objective function (although we can go higher than this)
# In practice, the penalty value also needs to be tuned. 
P = 1000
k = -1

# Construct facility constraints
for i in range(n):    
    terms_list.append(SlcTerm(
        c = P,
        terms = [
            Term(
                c = 1,
                indices = [variable_map[(i,j)]]
            )
        for j in range(n)
        ] + 
        [Term(c=k, indices=[])] #constant k term
    ))

# Construct location constraints
for i in range(n):    
    terms_list.append(SlcTerm(
        c = P,
        terms = [
            Term(
                c = 1,
                indices = [variable_map[(j,i)]]
            )
        for j in range(n)
        ] + 
        [Term(c=k, indices=[])] #constant k term
    ))

# Construct final problem with all the terms (monomial and slc)
problem = Problem(name="Small QAP", problem_type=ProblemType.pubo, terms=terms_list)

print(f"Number of monimial terms: {len(problem.terms)}, number of grouped terms: {len(problem.terms_slc)}")
print(f"\nGrouped terms: {problem.terms_slc}")

# Submitting problem to the Azure Quantum solver
# The SlcTerm functionality is available for all Microsoft QIO CPU solvers. 
# For this sample we will use the population annealing solver with its default parameters (since the problem is trivial).

solver = PopulationAnnealing(
    workspace,
    sweeps=10,
    seed=10
)

print('Submitting QAP...')
start = time.time()
result = solver.optimize(problem)
timeElapsed = time.time() - start
print('Result in {:.1f} seconds: '.format(timeElapsed), result["solutions"][0])


# The cost returned above should be 270.
# The solver returns a configuration mapped to the binary variables, but to interpret this, we need to map them back to the original variable definitions. 
solution = result["solutions"][0]
for v in variable_map:
    var_id = variable_map[v]
    if solution["configuration"][str(var_id)] == 1:
        print(f"Facility {v[0]} assigned to Location {v[1]}")
        


# ## Further Resources
# A public list of larger quadratic assignment problems can be found at [Cor\@l](https://coral.ise.lehigh.edu/data-sets/qaplib/) . 
# As an exercise, you can try converting them into Azure Quantum QIO form using the same method described above.
