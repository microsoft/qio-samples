---
page_type: sample
languages:
- python
author: adbai
ms.author: adbai@microsoft.com
ms.date: 09/09/2021
products:
- azure-quantum
- azure-qio
description: "Formulate and solve a quadratic assignment problem using optimization solvers with the Azure Quantum service"
urlFragment: azure-quantum.quadratic-assignment-problem
---

# Quadratic Assignment Problem (QAP) with optimization solvers and the Azure Quantum service

## Introduction

This sample provides a comprehensive walkthrough of the quadratic assignment problem, from problem definition to formulation of penalty functions and finally solving the problem using optimization solvers with the Azure Quantum service.

This sample also provides a demonstration on how to utilize the squared linear combination grouped terms functionality on the SDK. 

By working through this sample, you will learn:

- What the quadratic assignment problem is and how to convert it to unconstrained binary form
- How to build penalty expressions to represent problem constraints
- How to represent penalty expressions using the SlcTerm (Squared Linear Combination term) feature
- How to submit problem terms to Azure Quantum

## Prerequisites

1. [Create an Azure Quantum Workspace](https://docs.microsoft.com/azure/quantum/how-to-create-quantum-workspaces-with-the-azure-portal)
2. [Install the `azure-quantum` Python module](https://docs.microsoft.com/azure/quantum/optimization-install-sdk)
3. [Install Jupyter Notebook](https://jupyter.org/install)

## Running the sample

There are two ways to run the sample:

- [Jupyter Notebook (full sample walkthrough)](./quadratic-assignment-problem.ipynb)
- [Python Script (barebones annotations)](./quadratic-assignment-problem.py)

### Running the Jupyter Notebook

To run this sample, use the command line to navigate to the `quadratic-assignment-problem` folder and run `jupyter notebook`.

Simply click on the `quadratic-assignment-problem.ipynb` link to open the sample notebook.

### Running the Python script

- Open up the `quadratic-assignment-problem.py` script using your favorite IDE or a text editor.
- Fill in your Azure Quantum workspace details at the beginning of the script.
- Run the script through your IDE or use the command line to navigate to the `quadratic-assignment-problem` folder and then run `python ./quadratic-assignment-problem.py` or `python3 ./quadratic-assignment-problem.py` (depending on how your environment is set up).

### Manifest

- **[quadratic-assignment-problem.ipynb](https://github.com/microsoft/qio-samples/blob/main/samples/quadratic-assignment-problem/quadratic-assignment-problem.ipynb)**: Jupyter Notebook version of this sample.
- **[quadratic-assignment-problem.py](https://github.com/microsoft/qio-samples/blob/main/samples/quadratic-assignment-problem/quadratic-assignment-problem.py)**: Standalone Python version of this sample.
