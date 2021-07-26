# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

from azure.quantum.optimization import Solver, Problem, ProblemType, Term

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

# Define the problem
problem = Problem(name='problemName', problem_type=ProblemType.pubo)

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

# List of solvers that you want to iterate over
solvers_name = [
    "microsoft.tabu.cpu"
    ,"microsoft.qmc.cpu"
    ,"microsoft.simulatedannealing-parameterfree.cpu"
    # ,"microsoft.populationannealing.cpu"
    # ,"microsoft.SubstochasticMonteCarlo.cpu"
    ]

for solver_name in solvers_name:
    s = Solver(workspace, "Microsoft", solver_name, "microsoft.qio.v2", "microsoft.qio-results.v2")
    print("\nOptimizing with:", s.target)
    result = s.optimize(problem)
    print(result)
