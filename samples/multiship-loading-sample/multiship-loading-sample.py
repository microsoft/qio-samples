#!/usr/bin/env python
# coding: utf-8
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.


#  In this example, we will take our learnings from the ship-loading sample and generalize to load-balancing between any number of ships.
# 
#  We will use a PUBO format: indices are either 0 or 1 (-1 or 1 for Ising)
# 
#  In order to balance containers between multiple ships, one option is to define a cost function that:
#       1. Penalizes variance from a theoretical equal distribution (Equal Distribution = TotalContainerWeights / NbShips)
#       2. Penalizes the assignment of the same container on multiple ships
#
#   We will create two sub cost-functions H1 and H2 that we will then sum to evaluate the total cost of a solution
# 
#  1. Penalize variance from equal distribution between ships
#     A way to penalize a large variance from the equal distribution for a given ship is to express it in the following way:
#       Given 3 containers with respective weights W0, W1, W2 and EqDistrib = (W0 + W1 + W2) / 3
#           (W0 + W1 + W2 - EqDistrib)^2
# 
#   Let's take the following example:
# 
#   Cont. weights       1 5 9 7 3
#   Total weight        25
#   Ships               A, B, C
#   EquDistrib          25 / 3 = 8.33

#                   Containers
#                   1 5 9 7 3
#   Ship
#   A               0 0 9 0 0   (9-8.33 ) ^2    = 0.4489
#   B               0 5 0 0 3   (5+3-8.33)^2    = 0.1089
#   C               1 0 0 7 0   (1+7-8.33)^2    = 0.1089
#
#   As we need to represent our problem in a binary format we need to "encode" the presence (xi=1) or absence (xi=0) of a given container on a ship.
#       To do this, we need to have a label for the weight of each container on each ship. The table below shows how we assign this continuous index 
#       by repeating the list of container weights for each ship and assigning a single list of weight labels across all three ships:
#           Ship A            Ship B            Ship C
#           1  5  9  7  3  -  1  5  9  7  3  -  1   5   9   7   3
#           W0 W1 W2 W3 W4    W5 W6 W7 W8 W9    W10 W11 W12 W13 W14 
# 
#       The cost function H1 becomes: 
#           H1 = (W0.x0 + W1.x1 + W2.x2 + W3.x3 + W4.x4 - EqDistrib)^2                          --> For Ship A
#               + (W5.x5 + W6.x6 + W7.x7 + W8.x8 + W9.x9 - EqDistrib)^2                         --> For Ship B
#                   + (W10.x10 + W11.x11 + W12.x12 + W13.x13 + W14.x14 - EqDistrib)^2           --> For Ship C
# 
#       If you expand the above and group the common terms, you get the following:
#           W0^2.x0^2 + W1^2.x1^2 + W2^2.x2^2 + .... + W14^1.x14^14                           --> Term(w=Wi^2, indices=[i,i]
#               + 2(W0.x0 * W1.x1) + 2(W0.x0 * W2.x2) + 2(W0.x0 * W3.x3) + 2(W0.x0 * W4.x4)     --> Term(w=2*Wi*Wj, indices=[i,j])
#                   + 2(W1.x1 * W2.x2) + 2(W1.x1 * W3.x3) + 2(W1.x1 * W4.x4)
#                       + 2(W2.x2 * W3.x3) + 2(W2.x2 * W4.x4)
#                           + 2(W3.x3 * W4.x4)
#               + 2(W5.x5 * W6.x6) + 2(W5.x5 * W7.x7) + 2(W5.x5 * W8.x8) + 2(W5.x5 * W9.x9)
#                   + ...
#                       + ...
#                           + ...
#               + ...
#           - 2(W0.x0 * EqDistrib) - 2(W1.x1 * EqDistrib) - ... - 2(W14.x14 * EqDistrib)          --> Term(w=-2*Wi*EqDistrib, indices=[i])
# 
#  2. Penalize the assignment of the same container on multiple ships
#           Using the containers weight encoding in #1, we can devise a cost function such as this one for the first container:
#              (W0.x0 + W5.x5 + W10.x10 - W0)^2 
#           As W0, W5 and W10 are actually the same value (it is the same container represented across multiple ships)
#           we have: (W0.x0 + W0.x5 + W0.x10 - W0)^2
# 
#           If we expand and group the common terms, you get the following:
#               W0^2.x0^2 + W0^2.x5^2 + W0^2.x10^2
#                   + 2(W0^2.x0.x5) + 2(W0^2.x0.x10) + 2(W0^2.x5.x10)
#                       - 2(W0^2.x0) - 2(W0^2.x5) - 2(W0^2.x10)
#                           + W0^2                                                             --> The constant can be ignored as it is the same value for all solutions
# 
#           And you repeat the above for each container across all ships
#               H2 = W0^2.x0^2 + W1^2.x1^2 + .... + W14^2.x14^2                                --> Term(w=Wm^2, [m,m])
#                   + 2(W0^2.x0.x5) + 2(W0^2.x0.x10) + 2(W0^2.x5.x10) + ....                   --> Term(w=2*Wm^2, [m,n])
#                   + 2(W1^2.x1.x6) + 2(W1^2.x1.x11) + 2(W1^2.x6.x11)
#                   +
#                   ....
#                   + 2(W4^2.x4.x9) + 2(W4^2.x4.x14) + 2(W9^2.x9.x14)
#                   - 2(W0^2.x0) - 2(W1^2.x1) - .... - 2(W14^2.x14)                            --> Term(w=-2*Wm^2, [m])
# 
#   You will notice that H1 and H2 have common indices [i,i]/[m,m] and [i]/[m]
#   We will need to be careful to not duplicate them, but sum them, in our final list of Terms describing the cost function.
#   H = H1 + H2
#     =   2(W0^2.x0^2 + W1^2.x1^2 + .... + W14^2.x14^2)                                         --> Term(w=2*Wi^2, [i,i])
# 
#       - 2(W0^2.x0) - .... - 2(W4^2.x14) - (W0.x0 * EqDistrib) - ... - (W14.x14 * EqDistrib)   --> Term(w=-2Wi^2 - W0*EqDistrib, [i])
# 
#       + 2(W0^2.x0.x5) + 2(W0^2.x0.x10) + 2(W0^2.x5.x10)                                       --> Term(w=2*Wm^2, [m,n])
#       + ....
#       + 2(W4^2.x4.x9) + 2(W4^2.x4.x14) + 2(W9^2.x9.x14)
# 
#       + 2(W0.x0 * W1.x1) + 2(W0.x0 * W2.x2) + 2(W0.x0 * W3.x3) + 2(W0.x0 * W4.x4)             --> Term(w=2*Wi*Wj, indices=[i,j])
#           + 2(W1.x1 * W2.x2) + 2(W1.x1 * W3.x3) + 2(W1.x1 * W4.x4)
#               + 2(W2.x2 * W3.x3) + 2(W2.x2 * W4.x4)
#                   + 2(W3.x3 * W4.x4)
#           + 2(W5.x5 * W6.x6) + 2(W5.x5 * W7.x7) + 2(W5.x5 * W8.x8) + 2(W5.x5 * W9.x9)
#               + ...
#                   + ...
#                       + ...
# 

from typing import List
from azure.quantum.optimization import Problem, ProblemType, Term
import numpy as np
from itertools import combinations
from azure.quantum.optimization import ParallelTempering, SimulatedAnnealing, Tabu, HardwarePlatform, QuantumMonteCarlo
from azure.quantum.target.oneqbit import PathRelinkingSolver

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

def visualize_result(result, containers, ships, target):
    print("\rResult received from: ", target)
    nb_ships = len(ships)
    try:
        config = result['configuration']
        config = list(config.values())
        for ship, sub_config in enumerate(np.array_split(config, nb_ships)):
            shipWeight = 0
            for c,b in enumerate(sub_config):
                shipWeight = shipWeight + b*containers[c]
            print(f'Ship {ships[ship]}: \t' + ''.join(f'{b*containers[c]}' for c,b in enumerate(sub_config)) + ' - ' + str(shipWeight))
    except:
        print('No Configuration')
    try:
        print('Cost: {}'.format(result['cost']))
    except:
        print('No Cost')
    try:
        print('Parameters: {}'.format(result['parameters']))
    except:
        print('No Parameter')

def AddTermsWeightVarianceCost(start, end, containers, EqDistrib):
    terms: List[Term] = []
    for i,w in enumerate(containers[start:end+1], start):
        # -2*Wi*EqDistrib.xi -2Wi^2.xi (weight variance cost + duplicate container cost)
        terms.append(Term(w=-2*w*EqDistrib - 2*w*w, indices=[i]))
        # Wi^2.xi^2 + Wi^2.xi^2 (weight variance cost + duplicate container cost)
        terms.append(Term(w=2*w*w, indices=[i,i]))

    for c in combinations(range(start, end+1), 2):
        w0 = containers[c[0]]
        w1 = containers[c[1]]
        # 2*Wi*Wj (weight variance cost)
        terms.append(Term(w=2*w0*w1, indices=[c[0],c[1]]))

    return terms

def AddTermsDuplicateContainerCost(start, end, containers):
    terms: List[Term] = []

    # The following is integrated into AddTermsWeightVarianceCost to reduce the number of Terms and speed-up Terms generation
    # for c in combinations(range(start, end+1), 1):
    #     w = containers[c[0]][0]
    #     i1 = containers[c[0]][1]
    #     terms.append(Term(w=w*w, indices=[i1,i1]))              # Wi^2

    # 2.w^2.x_i.x_j terms
    for c in combinations(range(start, end+1), 2):
        w = containers[c[0]][0]
        i1 = containers[c[0]][1]
        i2 = containers[c[1]][1]
        terms.append(Term(w=2*w*w, indices=[i1,i2]))            # Term(w=2*Wm^2, [m,n])

    # The following is integrated into AddTermsWeightVarianceCost to reduce the number of Terms and speed-up Terms generation
    # # for c in combinations(range(start, end+1), 1):
    #     w = containers[c[0]][0]
    #     i1 = containers[c[0]][1]
    #     terms.append(Term(w=-2*w*w, indices=[i1]))              # -2*Wi^2

    # w^2 term
    terms.append(Term(w=containers[start][0]*containers[start][0], indices=[]))

    return terms

def createProblemForContainerWeights(containerWeights: List[int], Ships) -> List[Term]:

    terms: List[Term] = []
    containersWithinShip: List[int] = []
    containersAcrossShips: List[int, int] = []
    totalWeight = 0
    EqDistrib = 0

    for c in range (len(containerWeights)):
        totalWeight = totalWeight + containerWeights[c]
    EqDistrib = totalWeight / len(Ships)
    print(Ships)
    print(containerWeights)
    print("Total Weight:", totalWeight)
    print("Equal weight distribution:", EqDistrib)

    # Create container weights in this format:
    # 1  5  9  7  3  - 1  5  9  7  3  - 1   5   9   7   3
    # W0 W1 W2 W3 W4   W5 W6 W7 W8 W9   W10 W11 W12 W13 W14 
    containersWithinShip = containerWeights*len(Ships)

    # Create container weights in this format:
    # 1  1  1  5  5  5  9  9  9  7  7  7  3  3  3
    for i in range(len(containerWeights)):
        for j in range(len(Ships)):
            k = i + j*len(containerWeights)
            containersAcrossShips.append([containersWithinShip[i], k])

    for split in np.array_split(range(len(containersWithinShip)), len(Ships)):
        terms = terms + AddTermsWeightVarianceCost(split[0], split[-1], containersWithinShip, EqDistrib)

    for split in np.array_split(range(len(containersAcrossShips)), len(containerWeights)):
        terms = terms + AddTermsDuplicateContainerCost(split[0], split[-1], containersAcrossShips)

    return terms


# This array contains a list of the weights of the containers:
containerWeights = [3, 8, 3, 4, 1, 5, 2, 2, 7, 9, 5, 4, 8, 9, 4, 6, 8, 7, 6, 2, 2, 9, 4, 6, 3, 8, 5, 7, 2, 4, 9, 4]
Ships = ["A", "B", "C", "D", "E"]

# Create the Terms for this list of containers:
terms = createProblemForContainerWeights(containerWeights,Ships)

# Create the Problem to submit to the solver:
nbTerms = len(terms)
problemName = f'Balancing {str(len(containerWeights))} containers between {str(len(Ships))} Ships ({nbTerms:,} terms)'
print(problemName)
problem = Problem(name=problemName, problem_type=ProblemType.pubo, terms=terms)

def SolveMyProblem(problem, s):
    try:
        # Optimize the problem
        print("Optimizing with:", s.name)
        Job = s.submit(problem)
        Job.wait_until_completed()
        duration = Job.details.end_execution_time - Job.details.begin_execution_time
        if (Job.details.status == "Succeeded"):
            visualize_result(Job.get_results(), containerWeights*len(Ships), Ships, s.name)
            print("Execution duration: ", duration)
        else:
            print("\rJob ID", Job.id, "failed")
    except BaseException as e:
        print(e)

# Try to call a solver with different timeout value and see if it affects the results
SolveMyProblem(problem, SimulatedAnnealing(workspace, timeout=10))
# SolveMyProblem(problem, SimulatedAnnealing(workspace, timeout=20))
# SolveMyProblem(problem, SimulatedAnnealing(workspace, timeout=30))
# SolveMyProblem(problem, SimulatedAnnealing(workspace))

# Try using the parameters returned by the parameter free versions and observe the significant performance improvement
SolveMyProblem(problem, SimulatedAnnealing(workspace, timeout=5, beta_start=8.086689309396733e-05, beta_stop=7.594132985765675, restarts=360, sweeps=50))

SolveMyProblem(problem, Tabu(workspace, timeout=5))
# SolveMyProblem(problem, ParallelTempering(workspace, timeout=60))
# SolveMyProblem(problem, QuantumMonteCarlo(workspace))

# PathRelinkingSolver is only available if the 1QBit provider is enabled in your quantum workspace
# SolveMyProblem(problem, PathRelinkingSolver(workspace), -1)

