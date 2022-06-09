# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

# Note: Protobuf support is available for all Microsoft QIO CPU solvers
from azure.quantum.optimization import Problem, ProblemType, Term, ParallelTempering, PopulationAnnealing, QuantumMonteCarlo, SimulatedAnnealing, SubstochasticMonteCarlo, Tabu
from azure.quantum.job.base_job import ContentType

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

# Define the problem. Specify content type to use protobuf
problem = Problem(name="My First Problem", problem_type=ProblemType.ising, content_type=ContentType.protobuf)

terms = [
    Term(c=-9, indices=[0]),
    Term(c=-3, indices=[1,0]),
    Term(c=5, indices=[2,0]),
    Term(c=9, indices=[2,1]),
    Term(c=2, indices=[3,0]),
    Term(c=-4, indices=[3,1]),
    Term(c=4, indices=[3,2])
]

problem.add_terms(terms=terms)

# Create the solver
solver = PopulationAnnealing(workspace, timeout=100)

# Solve the problem
result = solver.optimize(problem)
print(result)