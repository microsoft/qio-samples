# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

from azure.quantum import Workspace
from azure.quantum.optimization import Problem, ProblemType, Term
from azure.quantum.target.toshiba import SimulatedBifurcationMachine

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

# Create Toshiba SQBM+ solver with default parameters
solver = SimulatedBifurcationMachine(workspace)

# Submit the problem for solving with Toshiba SQBM+
print("Submitting first problem (default params):")
result = solver.optimize(problem)

# Print out the result
print(result)

# Create Toshiba SQBM+ solver, specifically choosing to use the high-speed
# Ballistic Simulated Bifurcation algorithm (bSB), designed to find a good solution in a short time
# This is the default algorithm chosen if no 'algo' parameter is provided
solver = SimulatedBifurcationMachine(workspace, algo="1.5")

# Rename problem for easy differentiation later
problem.name = "bSB algorithm test problem"

# Submit the problem 
print("\nSubmitting bSB problem:")
result = solver.optimize(problem)
print(result)

# Create Toshiba SQBM+ solver, specifically choosing to use the high-accuracy 
# Discrete Simulated Bifurcation algorithm (dSB) which finds more accurate solutions
# at a calculation speed that surpasses that of other machines (https://www.science.org/doi/10.1126/sciadv.abe7953)
solver = SimulatedBifurcationMachine(workspace, algo="2.0")

# Rename problem for easy differentiation later
problem.name = "dSB algorithm test problem"

# Submit the problem 
print("\nSubmitting dSB problem:")
result = solver.optimize(problem)
print(result)

# Create Toshiba SQBM+ solver, making use of the auto-tune function provided
# which will select the best algorithm and parameters to use based on problem characteristics
solver = SimulatedBifurcationMachine(workspace, auto=True)

# Rename problem for easy differentiation later
problem.name = "auto-select algorithm test problem"

# Submit the problem 
print("\nSubmitting auto-select problem:")
result = solver.optimize(problem)
print(result)