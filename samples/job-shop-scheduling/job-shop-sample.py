#!/usr/bin/env python
# coding: utf-8

# Job Shop Scheduling Sample
## Job shop scheduling is a common and important problem in many industries. For example, in the automobile industry manufacturing a car involves many different types of operations which are performed by a number of specialized machines - optimizing the production line to minimize manufacturing time can make for significant cost savings. 

# Azure Quantum setup
## The Azure Quantum Optimization service is exposed via a Python SDK, which you will be making use of during the rest of this sample. This means that before you get started with formulating the problem, you first need to import some Python modules and set up an Azure Quantum `Workspace`.
## You will need to enter your Azure Quantum workspace details below:

from typing import List
from azure.quantum.optimization import Term
from azure.quantum import Workspace

workspace = Workspace (
    subscription_id = "",  # Add your subscription_id
    resource_group = "",   # Add your resource_group
    name = "",             # Add your workspace name
    location = ""          # Add your workspace location (for example, "westus")
)

workspace.login()

# Precedence constraint
def precedence_constraint(jobs_ops_map:dict, T:int, processing_time:dict, weight:float):
    """
    Construct penalty terms for the precedence constraint.

    Keyword arguments:

    jobs_ops_map (dict): Map of jobs to operations {job: [operations]}
    T (int): Allowed time (jobs can only be scheduled below this limit)
    processing_time (dict): Operation processing times
    weight (float): Relative importance of this constraint
    """

    terms = []

    # Loop through all jobs:
    for ops in jobs_ops_map.values():
        # Loop through all operations in this job:
        for i in range(len(ops) - 1):
            for t in range(0, T):
                # Loop over times that would violate the constraint:
                for s in range(0, min(t + processing_time[ops[i]], T)):
                    # Assign penalty
                    terms.append(Term(c=weight, indices=[ops[i]*T+t, (ops[i+1])*T+s]))

    return terms

# Operation once constraint
def operation_once_constraint(ops_jobs_map:dict, T:int, weight:float):
    """
    Construct penalty terms for the operation once constraint.
    Penalty function is of form: 2xy - x - y + 1

    Keyword arguments:

    ops_jobs_map (dict): Map of operations to jobs {op: job}
    T (int): Allowed time (jobs can only be scheduled below this limit)
    weight (float): Relative importance of this constraint
    """

    terms = []

    # 2xy - x - y parts of the constraint function
    # Loop through all operations
    for op in ops_jobs_map.keys():
        for t in range(T):
            # - x - y terms
            terms.append(Term(c=weight*-1, indices=[op*T+t]))

            # + 2xy term
            # Loop through all other start times for the same job
            # to get the cross terms
            for s in range(t+1, T):
                terms.append(Term(c=weight*2, indices=[op*T+t, op*T+s]))

    # + 1 term
    terms.append(Term(c=weight*1, indices=[]))

    return terms


# No-overlap constraint
def no_overlap_constraint(T:int, processing_time:dict, ops_jobs_map:dict, machines_ops_map:dict, weight:float):
    """
    Construct penalty terms for the no overlap constraint.

    Keyword arguments:

    T (int): Allowed time (jobs can only be scheduled below this limit)
    processing_time (dict): Operation processing times
    weight (float): Relative importance of this constraint
    ops_jobs_map (dict): Map of operations to jobs {op: job}
    machines_ops_map(dict): Mapping of operations to machines, e.g.:
        machines_ops_map = {
            0: [0,1],          # Operations 0 & 1 assigned to machine 0
            1: [2,3]           # Operations 2 & 3 assigned to machine 1
        }
    """

    terms = []

    # For each machine
    for ops in machines_ops_map.values():
        # Loop over each operation i requiring this machine
        for i in ops:
            # Loop over each operation k requiring this machine 
            for k in ops:
                # Loop over simulation time
                for t in range(T):
                    # When i != k (when scheduling two different operations)
                    if i != k:
                        # t = s meaning two operations are scheduled to start at the same time on the same machine
                        terms.append(Term(c=weight*1, indices=[i*T+t, k*T+t]))

                        # Add penalty when operation runtimes overlap
                        for s in range(t, min(t + processing_time[i], T)):
                            terms.append(Term(c=weight*1, indices=[i*T+t, k*T+s]))  

                        # If operations are in the same job, penalize for the extra time 0 -> t (operations scheduled out of order)
                        if ops_jobs_map[i] == ops_jobs_map[k]:
                            for s in range(0, t):
                                if i < k:
                                    terms.append(Term(c=weight*1, indices=[i*T+t, k*T+s]))  
                                if i > k:
                                    terms.append(Term(c=weight*1, indices=[i*T+s, k*T+t]))  

    return terms


# Minimize the makespan
def calc_penalty(t:int, m_count:int, t0:int): 
    assert m_count > 1                           # Ensure you don't divide by 0
    return (m_count**(t - t0) - 1)/float(m_count - 1)

def makespan_objective(T:int, processing_time:dict, jobs_ops_map:dict, m_count:int, weight:float):
    """
    Construct makespan minimization terms.

    Keyword arguments:

    T (int): Allowed time (jobs can only be scheduled below this limit)
    processing_time (dict): Operation processing times
    jobs_ops_map (dict): Map of jobs to operations {job: [operations]}
    m_count (int): Number of machines
    weight (float): Relative importance of this constraint
    """

    terms = []

    lower_bound = max([sum([processing_time[i] for i in job]) for job in jobs_ops_map.values()])
    upper_bound = T

    # Loop through the final operation of each job
    for job in jobs_ops_map.values():
        i = job[-1]
        # Loop through each time step the operation could be completion at
        for t in range(lower_bound + 1, T + processing_time[i]):
            terms.append(Term(c=weight*(calc_penalty(t, m_count, lower_bound)), indices=[i*T + (t - processing_time[i])]))

    return terms

# Putting it all together
def process_config(jobs_ops_map:dict, machines_ops_map:dict, processing_time:dict, T:int):
    """
    Process & validate problem parameters (config) and generate inverse dict of operations to jobs.

    Keyword arguments:
    
    jobs_ops_map (dict): Map of jobs to operations {job: [operations]}
    machines_ops_map(dict): Mapping of operations to machines, e.g.:
        machines_ops_map = {
            0: [0,1],          # Operations 0 & 1 assigned to machine 0
            1: [2,3]           # Operations 2 & 3 assigned to machine 1
        }
    processing_time (dict): Operation processing times
    T (int): Allowed time (jobs can only be scheduled below this limit)
    """

    # Problem cannot take longer to complete than all operations executed sequentially
    ## Sum all operation processing times to calculate the maximum makespan
    T = min(sum(processing_time.values()), T) 

    # Ensure operation assignments to machines are sorted in ascending order
    for m, ops in machines_ops_map.items():
        machines_ops_map[m] = sorted(ops)
    ops_jobs_map = {}

    for job, ops in jobs_ops_map.items():
        # Fail if operation IDs within a job are out of order
        assert (ops == sorted(ops)), f"Operation IDs within a job must be in ascending order. Job was: {job}: {ops}"

        for op in ops:
            # Fail if there are duplicate operation IDs
            assert (op not in ops_jobs_map.keys()), f"Operation IDs must be unique. Duplicate ID was: {op}"
            ops_jobs_map[op] = job

    return ops_jobs_map, T

# Set problem parameters
## Allowed time (jobs can only be scheduled below this limit)
T = 21 

## Processing time for each operation
processing_time = {0: 2, 1: 1, 2: 3, 3: 2, 4: 2, 5: 3, 6: 1, 7: 2, 8: 3, 9: 2}

## Assignment of operations to jobs (job ID: [operation IDs])
### Operation IDs within a job must be in ascending order
jobs_ops_map = {
    0: [0, 1, 2],
    1: [3, 4, 5],
    2: [6, 7, 8, 9]
}

## Assignment of operations to machines
### Three jobs, two machines
machines_ops_map = {
    0: [0, 1, 3, 4, 6, 7],  # Operations 0, 1, 3, 4, 6 and 7 are assigned to machine 0 (the computer)
    1: [2, 5, 8],           # Operations 2, 5 and 8 are assigned to machine 1 (the printer)
    2: [9]                  # Operation 9 is assigned to machine 2 (the tooth floss)
}

## Inverse mapping of jobs to operations
ops_jobs_map, T = process_config(jobs_ops_map, machines_ops_map, processing_time, T)


# The following code snippet shows how you assign weight values and assemble the penalty terms by summing the output of the penalty and objective functions. 
# These terms represent the cost function and they are what you will submit to the solver.

# Generate terms to submit to solver using functions defined previously
## Assign penalty term weights:
alpha = 1  # Precedence constraint
beta = 1   # Operation once constraint
gamma = 1  # No overlap constraint
delta = 0.00000005  # Makespan minimization (objective function)

## Build terms
### Constraints:
c1 = precedence_constraint(jobs_ops_map, T, processing_time, alpha)
c2 = operation_once_constraint(ops_jobs_map, T, beta)
c3 = no_overlap_constraint(T, processing_time, ops_jobs_map, machines_ops_map, gamma)

### Objective function
c4 = makespan_objective(T, processing_time, jobs_ops_map, len(machines_ops_map), delta)

### Combine terms:
terms = []
terms = c1 + c2 + c3 + c4

from azure.quantum.optimization import Problem, ProblemType
from azure.quantum.optimization import SimulatedAnnealing # Change this line to match the Azure Quantum Optimization solver type you wish to use

# Problem type is PUBO in this instance. You could also have chosen to represent the problem in Ising form.
problem = Problem(name="Job shop sample", problem_type=ProblemType.pubo, terms=terms)

# Provide details of your workspace, created at the beginning of this tutorial
# Provide the name of the solver you wish to use for this problem (as imported above)
solver = SimulatedAnnealing(workspace, timeout = 100) # Timeout in seconds

# Run job synchronously
result = solver.optimize(problem)
config = result['configuration']

# Run job asynchronously
# Alternatively, a job can be run asynchronously, as shown below:

"""
## Submit problem to solver
job = solver.submit(problem)
print(job.id)

## Get job status
job.refresh()
print(job.details.status)

## Get results
result = job.get_results()
config = result['configuration']
"""

# Map variables to operations
# This code snippet contains several helper functions which are used to parse the results returned from the solver and print them to screen in a user-friendly format.
def create_op_array(config: dict):
    """
    Create array from returned config dict.
    
    Keyword arguments:
    config (dictionary): config returned from solver
    """

    variables = []
    for key, val in config.items():
        variables.insert(int(key), val)
    return variables

def print_problem_details(ops_jobs_map:dict, processing_time:dict, machines_ops_map:dict):
    """
    
    Print problem details e.g. operation runtimes and machine assignments.        
    
    Keyword arguments:
    ops_jobs_map (dict): Map of operations to jobs {operation: job}
    processing_time (dict): Operation processing times
    machines_ops_map(dict): Mapping of machines to operations
    """

    machines = [None] * len(ops_jobs_map)

    for m, ops in machines_ops_map.items():
        for op in ops:
          machines[op] = m
    
    print(f"           Job ID: {list(ops_jobs_map.values())}")
    print(f"     Operation ID: {list(ops_jobs_map.keys())}")
    print(f"Operation runtime: {list(processing_time.values())}")
    print(f" Assigned machine: {machines}")
    print()
    
def split_array(T:int, array:List[int]):
    """
    Split array into rows representing the rows of our operation matrix.
        
    Keyword arguments:
    T (int): Time allowed to complete all operations
    array (List[int]): array of x_i,t values generated from config returned by solver
    """

    ops = []
    i = 0
    while i < len(array):
        x = array[i:i+T]
        ops.append(x)
        i = i + T
    return ops

def print_matrix(T:int, matrix:List[List[int]]):
    """
    Print final output matrix.        
    
    Keyword arguments:
    T (int): Time allowed to complete all operations
    matrix (List[List[int]]): Matrix of x_i,t values
    """

    labels = "    t:"
    for t in range(0, T):
        labels += f" {t}"
    print(labels)
    
    idx = 0
    for row in matrix:
        print("x_" + str(idx) + ",t: ", end="")
        print(' '.join(map(str,row)))
        idx += 1
    print()

def extract_start_times(jobs_ops_map:dict, matrix:List[List[int]]):
    """
    Extract operation start times & group them into jobs.
    
    Keyword arguments:
    jobs_ops_map (dict): Map of jobs to operations {job: [operations]}
    matrix (List[List[int]]): Matrix of x_i,t values
    """
    #jobs = {}
    jobs = [None] * len(jobs_ops_map)
    op_start_times = []
    for job, ops in jobs_ops_map.items(): 
        x = [None] * len(ops)
        for i in range(len(ops)):
            try :
                x[i] = matrix[ops[i]].index(1)
                op_start_times.append(matrix[ops[i]].index(1))
            except ValueError:
                x[i] = -1
                op_start_times.append(-1)
        jobs[job] = x

    return jobs, op_start_times


# Results
# Produce 1D array of x_i,t = 0, 1 representing when each operation starts
op_array = create_op_array(config) 

# Print config details:
print(f"\nConfig dict:\n{config}\n")
print(f"Config array:\n{op_array}\n")

# Print problem setup
print_problem_details(ops_jobs_map, processing_time, machines_ops_map)

# Print final operation matrix, using the returned config
print("Operation matrix:")
matrix = split_array(T, op_array) 
print_matrix(T, matrix)

# Find where each operation starts (when x_i,t = 1) and return the start time
print("Operation start times (grouped into jobs):")
jobs, op_start_times = extract_start_times(jobs_ops_map, matrix)
print(jobs)

# Calculate makespan (time taken to complete all operations - the objective you are minimizing)
op_end_times = [op_start_times[i] + processing_time[i] for i in range(len(op_start_times))]
makespan = max(op_end_times)

print(f"\nMakespan (time taken to complete all operations): {makespan}\n")


# For this small problem instance, the solver quickly returned a solution. For bigger, more complex problems you may need to run the job asynchronously, as shown earlier in this sample.

# Validate the solution
def check_precedence(processing_time, jobs):
    """    
    Check if the solution violates the precedence constraint.
    Returns True if the constraint is violated.       
    
    Keyword arguments:
    processing_time (dict): Operation processing times
    jobs (List[List[int]]): List of operation start times, grouped into jobs
    """

    op_id = 0
    for job in jobs:
        for i in range(len(job) - 1):
            if job[i+1] - job[i] < processing_time[op_id]:
                return True
            op_id += 1
        op_id += 1
    return False
    
def check_operation_once(matrix):
    """    
    Check if the solution violates the operation once constraint.
    Returns True if the constraint is violated.       
    
    Keyword arguments:
    matrix (List[List[int]]): Matrix of x_i,t values
    """
    for x_it_vals in matrix:
        if sum(x_it_vals) != 1:
            return True
    return False

def check_no_overlap(op_start_times:list, machines_ops_map:dict, processing_time:dict):
    """    
    Check if the solution violates the no overlap constraint.
    Returns True if the constraint is violated.       
    
    Keyword arguments:
    op_start_times (list): Start times for the operations
    machines_ops_map(dict): Mapping of machines to operations
    processing_time (dict): Operation processing times
    """
    pvals = list(processing_time.values())

    # For each machine
    for ops in machines_ops_map.values():
        machine_start_times = [op_start_times[i] for i in ops]
        machine_pvals = [pvals[i] for i in ops]

        # Two operations start at the same time on the same machine
        if len(machine_start_times) != len(set(machine_start_times)):
            return True
        
        # There is overlap in the runtimes of two operations assigned to the same machine
        machine_start_times, machine_pvals = zip(*sorted(zip(machine_start_times, machine_pvals)))
        for i in range(len(machine_pvals) - 1):
            if machine_start_times[i] + machine_pvals[i] > machine_start_times[i+1]:
                return True

    return False
    
def validate_solution(matrix:dict, machines_ops_map:dict, processing_time:dict, jobs_ops_map:dict):
    """    
    Check that solution has not violated any constraints. 
    Returns True if the solution is valid.       
    
    Keyword arguments:
    matrix (List[List[int]]): Matrix of x_i,t values
    machines_ops_map(dict): Mapping of machines to operations
    processing_time (dict): Operation processing times
    jobs_ops_map (dict): Map of jobs to operations {job: [operations]}
    """

    jobs, op_start_times = extract_start_times(jobs_ops_map, matrix)

    # Check if constraints are violated
    precedence_violated = check_precedence(processing_time, jobs)
    operation_once_violated = check_operation_once(matrix)
    no_overlap_violated = check_no_overlap(op_start_times, machines_ops_map, processing_time)
    
    if not precedence_violated and not operation_once_violated and not no_overlap_violated:
        print("Solution is valid.\n")
    else:
        print("Solution not valid. Details:")
        print(f"\tPrecedence constraint violated: {precedence_violated}")
        print(f"\tOperation once constraint violated: {operation_once_violated}")
        print(f"\tNo overlap constraint violated: {no_overlap_violated}\n")

validate_solution(matrix, machines_ops_map, processing_time, jobs_ops_map)
