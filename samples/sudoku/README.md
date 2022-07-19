---
page_type: sample
languages:
- python
author: Maximilian Lucassen
ms.author: maxlucassen@microsoft.com
ms.date: 4/22/2022
products:
- azure-quantum
- azure-qio
description: "Solve sudokus with Azure Quantum service"
urlFragment: azure-quantum.sudoku
---

# Solving sudokus using optimization solvers with the Azure Quantum service

## Introduction

This sample provides a walkthrough on how to solve sudokus with Microsoft QIO solvers and the Azure Quantum service, from problem definition to formulation of constraints to submitting the problem to the Azure Quantum service.

By working through this sample, you will learn:

- How to solve sudokus with Azure Quantum
- Model the problem mathematically to design objective and penalty functions
- Coding of the optimization problem using the Azure Quantum Python SDK
- Verifying results returned by the solver

## Prerequisites

1. [Create an Azure Quantum Workspace](https://docs.microsoft.com/azure/quantum/how-to-create-quantum-workspaces-with-the-azure-portal)
2. [Install the `azure-quantum` Python module](https://docs.microsoft.com/azure/quantum/optimization-install-sdk)
3. (If you want to run the Jupyter notebook) [Install Jupyter Notebook](https://jupyter.org/install)
4. (Optional) [Run the basic ship loading sample](../ship-loading/)

## Running the sample

There are two ways to run the sample (.ipynb and .py):

- [Jupyter Notebook (step-by-step walkthrough)](./SudokuSolver.ipynb)
- [Python script (barebones annotations)](./SudokuSolver.py)

A html file of the Jupyter notebook is attached for improved readability:

- [Html page (more readable format than Jupyter Notebook)](./SudokuSolver.html)

### Running the Jupyter Notebook

To run this sample, use the command line to navigate to the `sudoku` folder and run `jupyter notebook`

Your web browser should automatically open a new window.

If this doesn't happen, copy the localhost link shown in the terminal window and paste it into your browser's address bar.

Once you see the page above, simply click on the `SudokuSolver.ipynb` link to open the sample notebook.

### Running the Python script

- Open up the `SudokuSolver.py` script using your favorite IDE or a text editor.
- Fill in your Azure Quantum workspace details at the beginning of the script.
- Run the script through your IDE or use the command line to navigate to the `sudoku` folder and then run `python ./SudokuSolver.py` or `python3 ./SudokuSolver.py` (depending on how your environment is set up).

### Manifest

- **[SudokuSolver.ipynb](https://github.com/microsoft/qio-samples/blob/main/samples/sudoku/SudokuSolver.ipynb)**: Jupyter Notebook version of this sample.
- **[SudokuSolverpy](https://github.com/microsoft/qio-samples/blob/main/samples/sudoku/SudokuSolver.py)**: Standalone Python version of this sample.
- **[SudokuSolver.html](https://github.com/microsoft/qio-samples/blob/main/samples/sudoku/SudokuSolver.html)**: HTML version of this sample.

