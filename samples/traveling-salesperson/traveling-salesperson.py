#!/usr/bin/env python
# coding: utf-8

# Import dependencies
import numpy as np
import os
import time
import math
import requests
import json
import datetime  

from azure.quantum.optimization import Problem, ProblemType, Term, Solver
from azure.quantum.optimization import SimulatedAnnealing, ParallelTempering, Tabu, QuantumMonteCarlo
from typing import List

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

### Define variables

# The number of nodes
NumNodes = 5

# Max cost between nodes 
maxCost = 10

# Node names, to interpret the solution later on
NodeName = {0:'A', 1:'B', 2:'C', 3:'D', 4:'E', 5:'F', 6:'G', 7:'H', 8:'I', 9:'J', 10:'K', 
            11:'L', 12:'M', 13:'N', 14:'O', 15:'P', 16:'Q', 17:'R', 18:'S', 19:'T',
            20:'U', 21:'V', 22:'W', 23:'X', 24:'Y', 25:'Z'}

# Cost to travel between nodes -- note this matrix is not symmetric (traveling A->B is not same as B->A!)
CostMatrix = np.array([[1, 4, 7, 4, 3], [3, 3, 3, 1, 2], [2, 5, 2, 3, 1], [7, 8, 1, 3, 5], [3, 2, 1, 9, 8]])    # If you want to rerun with the same matrix
#CostMatrix = np.random.randint(maxCost, size=(NumNodes,NumNodes))                                          # If you want to run with a new cost matrix
 
############################################################################################
##### Define the optimization problem for the Quantum Inspired Solver
def OptProblem(CostMatrix) -> Problem:
    
    #'terms' will contain the weighting terms for the trips!
    terms = []

    ############################################################################################
    ##### Cost of traveling between nodes  
    for k in range(0, len(CostMatrix)):                          # For each trip
        for i in range(0, len(CostMatrix)):                      # For each origin node
            for j in range(0, len(CostMatrix)):                  # For each destination node
                
                #Assign a weight to every possible trip from node i to node j for each trip 
                terms.append(
                    Term(
                        c = CostMatrix.item((i,j)),                                     # Element of the cost matrix
                        indices = [i + (len(CostMatrix) *k ), j + (len(CostMatrix) * (k + 1))]    # +1 to denote dependence on next location
                    )
                )
                ##----- Uncomment one of the below statements if you want to see how the weights are assigned! -------------------------------------------------------------------------------------------------
                #print(f'{i + (len(CostMatrix) * k)}, {j + (len(CostMatrix) * (k + 1))}')                                                                   # Combinations between the origin and destination nodes 
                #print(f'For x_{i + (len(CostMatrix) * k)}, to x_{j + (len(CostMatrix) * (k + 1))} in trip number {k} costs: {CostMatrix.item((i,j))}')     # In a format for the solver (as formulated in the cost function)
                #print(f'For node_{i}, to node_{j} in trip number {k} costs: {CostMatrix.item((i,j))}')                                                     # In a format that is easier to read for a human
    
    ############################################################################################
    ##### Constraint: Location constraint - salesperson can only be at 1 node at a time.
    for l in range(0,len(CostMatrix)+1):                # The total number of nodes that are visited over the route (+1 because returning to starting node)
        for i in range(0,len(CostMatrix)):              # For each origin node
            for j in range(0,len(CostMatrix)):          # For each destination node
                if i!=j and i<j:                        # i<j because we don't want to penalize twice // i==j is forbidden (above)
                    terms.append(
                        Term(
                            c = int(2 * np.max(CostMatrix)),                                     # Assign a weight penalty dependent on maximum distance from the cost matrix elements
                            indices = [i + (len(CostMatrix) * l), j + (len(CostMatrix) * l)]                   
                        )
                    )
                    ##----- Uncomment one of the below statements if you want to see how the weights are assigned! -------------------------------------------------------------------------------------------------
                    #print(f'{i + (len(CostMatrix) * k)}, {j + (len(CostMatrix) * (k))}')
                    #print(f'Location constraint 1: x_{i + (len(CostMatrix) * l)} - x_{j + (len(CostMatrix) * (l + 1))} (trip {l}) assigned weight: {int(2 * np.max(CostMatrix))}')  # In a format for the solver (as formulated in the cost function)
    
    ############################################################################################
    ##### Constraint: Location constraint - encourage the salesperson to be 'somewhere' otherwise all x_k might be 0 (for example).
    for v in range(0, len(CostMatrix) + len(CostMatrix) * (len(CostMatrix))):    # Select variable (v represents a node before/after any trip)
        terms.append(
            Term(
                c = int(-1.65 * np.max(CostMatrix)),          # Assign a weight penalty dependent on maximum distance from the cost matrix elements
                indices = [v]   
            )
        )
        ##----- Uncomment one of the below statements if you want to see how the weights are assigned! -------------------------------------------------------------------------------------------------
        #print(v)
        #print(f'Location constraint 2: x_{v} assigned weight: {int(-1.65 * np.max(CostMatrix))}')                                                      # In a format for the solver (as formulated in the cost function)
        #print(f'Location constraint 2: node_{v % NumNodes} after {np.floor(v / NumNodes)} trips assigned weight: {int(-1.65 * np.max(CostMatrix))}')   # In a format that is easier to read for a human

    ############################################################################################                        
    ##### Penalty for traveling to the same node again --- (in the last step we can travel without penalties (this is to make it easier to specify an end node =) ))
    for p in range(0, len(CostMatrix) + len(CostMatrix) * (len(CostMatrix))):                                  # This selects a present node x: 'p' for present    
        for f in range(p + len(CostMatrix), len(CostMatrix) * (len(CostMatrix)), len(CostMatrix)):              # This selects the same node x but after upcoming trips: 'f' for future
            terms.append(
                Term(
                    c = int(2 * np.max(CostMatrix)),                               # assign a weight penalty dependent on maximum distance from the cost matrix elements
                    indices = [p,f]   
                )
            )     
            ##----- Uncomment one of the below statements if you want to see how the weights are assigned! -------------------------------------------------------------------------------------------------
            #print(f'x_{p}, x_{f}')                                                                                                                                             # Just variable numbers 
            #print(f'Visit once constraint: x_{p} - x_{f}  assigned weight: {int(2 * np.max(CostMatrix))}')                                                                     # In a format for the solver (as formulated in the cost function)
            #print(f' Visit once constraint: node_{p % NumNodes} - node_{(p + f) % NumNodes} after {(f - p) / NumNodes} trips assigned weight: {int(2 * np.max(CostMatrix))}')  # In a format that is easier to read for a human


    #############################################################################################                        
    ##### Begin at x0
    terms.append(
        Term(
            c = int(-10 * np.max(CostMatrix)),                   # Assign a weight penalty dependent on maximum distance from the cost matrix elements
            indices = [0]   
        )
    )

    ############################################################################################                        
    ##### End at x0
    terms.append(
        Term(
            c = int(-10 * np.max(CostMatrix)),                   # Assign a weight penalty dependent on maximum distance from the cost matrix elements
            indices = [len(CostMatrix) * (len(CostMatrix))]   
        )    
    )

    return Problem(name="Traveling Salesperson", problem_type=ProblemType.pubo, terms=terms)

# Parse the results

############################################################################################
##### Read the results returned by the solver - need to make the solution readable
def ReadResults(Config: dict, NodeName, CostMatrix, NumNodes):  

    #############################################################################################
    ##### Read the return result (dictionary) from the solver and sort it
    PathChoice = Config.items()
    PathChoice = [(int(k), v) for k, v in Config.items()] 
    PathChoice.sort(key=lambda tup: tup[0]) 

    #############################################################################################
    ##### Initialize variables to understand the routing    
    TimeStep=[]                                                     # This will contain an array of times/trips - each node is represented during/for each time/trip interval
    Node = []                                                       # This will contain an array of node names 
    Location = []                                                   # This will contain the locations the salesperson is for each time/trip
    RouteMatrixElements = []                                        # This will contain the indices of the cost matrix representing where the salesperson has traveled (to determine total cost)

    #############################################################################################
    ##### Go through nodes during each timestep/trip to see where the salesperson has been
    for Index in PathChoice:
        TimeStep.append(math.floor(Index[0] / len(CostMatrix)))         # Time step/trip = the k-th is floor of the index divided by the number of nodes
        Node.append(NodeName[(Index[0] % len(CostMatrix))])             # Append node names for each time step
        Location.append(Index[1])                                       # Append locations for each time step
        if Index[1] == 1:                                               # Save selected node where the salesperson travels to in that trip (if the variable == 1, the salesperson goes to that node)
            RouteMatrixElements.append(Index[0] % len(CostMatrix))      # Save the indices (this returns the row index)
    SimulationResult = np.array([TimeStep, Node, Location])             # Save all the route data (also where the salesperson did not go during a turn/trip/timestep)
 
    #############################################################################################
    ##### Create the route dictionary 
    k=0                                                                                                             
    PathDict = {}                                                                                                                                              
    PathDict['Route'] = {}
    Path = np.array([['Timestep,', 'Node']])
    for i in range(0, (NumNodes * (NumNodes + 1))):
        if SimulationResult[2][i] == '1':                                                                       # If the SimulationResult[2][i] (location) == 1, then that's where the salesperson goes/went
            Path = np.concatenate((Path, np.array([[SimulationResult[j][i] for j in range(0, 2)]])), axis=0)    # Add the rows where the salesperson DOES travel to Path matrix
            PathDict['Route'].update({k: Path[k + 1][1]})                                                       # Save the route to a dictionary
            k += 1                                                                                              # Iterable keeps track for the dictionary, but also allows to check for constraint
    AnalyzeResult(Path, NumNodes)                                                                               # Check if Path array satisfies other constraints as well (could integrate previous one above in function)

    #############################################################################################
    ###### Calculate the total cost of the route the salesperson made (can be in time (minutes) or in distance (km))
    TotalRouteCost = 0
    for trips in range(0, NumNodes):
        TotalRouteCost = TotalRouteCost+float(CostMatrix.item(RouteMatrixElements[trips], RouteMatrixElements[trips + 1]))     # The sum of the matrix elements where the salesperson has been (determined through the indices)
    PathDict['RouteCost'] = {'Cost':TotalRouteCost}

    ##### Return the simulation result in a human understandable way =)
    return PathDict


############################################################################################
##### Check whether the solution satisfies the optimization constraints 
def AnalyzeResult(Path, NumNodes):

    ############################################################################################                        
    ##### Check if the number of travels is equal to the number of nodes + 1 (for returning home)
    if (len(Path) - 1) != NumNodes + 1:
        raise RuntimeError('This solution is not valid -- Number of nodes visited invalid!')
    else:
        NumNodesPassed = NumNodes
        print(f"Number of nodes passed = {NumNodesPassed}. This is valid!")

    ############################################################################################                        
    ##### Check if the nodes are different (except start/end node)
    PastNodes = []
    for k in range(1, len(Path) - 1):                                                                           # Start to second last node must all be different - skip header so start at 1, skip last node so - 1
        for l in range(0, len(PastNodes)):  
            if Path[k][1] == PastNodes[l]:
                raise RuntimeError('This solution is not valid -- Traveled to a non-starting node more than once')
        PastNodes.append(Path[k][1])
    print(f"Number of different nodes passed = {NumNodes}. This is valid!") 

    ############################################################################################                        
    ##### Check if the end node is same as the start node
    if Path[1][1] != Path[-1][1]:
        raise RuntimeError(f'This solution is not valid -- Start node {Path[1][1]} is not equal to end node {Path[-1][1]}')
    print('Start and end node are the same. This is valid!')


    print('Valid route!')

############################################################################################
# Generate cost function
OptimizationProblem = OptProblem(CostMatrix)

# Choose the solver and parameters --- uncomment if you wish to use a different one

solver = SimulatedAnnealing(workspace, timeout = 120)   
#solver = ParallelTempering(workspace, timeout = 120)
#solver = Tabu(workspace, timeout = 120)
#solver = QuantumMonteCarlo(workspace, sweeps = 2, trotter_number = 10, restarts = 72, seed = 22, beta_start = 0.1, transverse_field_start = 10, transverse_field_stop = 0.1) # QMC is not available parameter-free yet

route = solver.optimize(OptimizationProblem)                                        # Synchronously submit the optimization problem to the service -- wait until done.
print(route)

# Call the function to interpret/convert/analyze the optimization results into a more meaningful/understandable format
PathDict = ReadResults(route['configuration'], NodeName, CostMatrix, NumNodes)
print(PathDict)
