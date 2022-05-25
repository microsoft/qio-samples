# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

from azure.quantum import Workspace
from azure.quantum.optimization import Problem, ProblemType, Term
from azure.quantum.optimization.toshiba import SimulatedBifurcationMachine

# Copy the settings for your workspace below
workspace = Workspace(
    resource_id = "",   # add the Resource ID of the Azure Quantum workspace you created with the Toshiba provider
    location = ""
)

# Define the problem
problem = Problem(name="My First Toshiba SQBM+ Problem", problem_type=ProblemType.pubo)

problem.add_terms([
    Term(w=-9, indices=[0]),
    Term(w=-3, indices=[1,0]),
    Term(w=5, indices=[2,0]),
    Term(w=9, indices=[2,1]),
    Term(w=2, indices=[3,0]),
    Term(w=-4, indices=[3,1]),
    Term(w=4, indices=[3,2])
])

# Create Toshiba SQBM+ solver
solver = SimulatedBifurcationMachine(workspace)

# Submit the problem for solving with Toshiba SQBM+
result = solver.optimize(problem)

# Print out the result
print(result)