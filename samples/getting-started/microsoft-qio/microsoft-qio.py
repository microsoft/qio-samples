from azure.quantum import Workspace
from azure.quantum.optimization import Problem, ProblemType, Term, ParallelTempering

# Workspace information
workspace = Workspace(
    subscription_id = "",  # Add your subscription_id
    resource_group = "",   # Add your resource_group
    name = "",             # Add your workspace name
    location = ""          # Add your workspace location (for example, "westus")
)

# Login
workspace.login()

# Define the problem
problem = Problem(name="My First Problem", problem_type=ProblemType.ising)

terms = [
    Term(w=-9, indices=[0]),
    Term(w=-3, indices=[1,0]),
    Term(w=5, indices=[2,0]),
    Term(w=9, indices=[2,1]),
    Term(w=2, indices=[3,0]),
    Term(w=-4, indices=[3,1]),
    Term(w=4, indices=[3,2])
]

problem.add_terms(terms=terms)

# Create the solver
solver = ParallelTempering(workspace, timeout=100)

# Solve the problem
result = solver.optimize(problem)
print(result)