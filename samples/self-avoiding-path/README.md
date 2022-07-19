---
page_type: sample
languages:
- python
author: Maximilian Lucassen
ms.author: maxlucassen@microsoft.com
ms.date: 7/19/2022
products:
- azure-quantum
- azure-qio
description: "Solve the self-avoiding path problem with Azure Quantum optimization service"
urlFragment: azure-quantum.self-avoiding-path
---

# Solving self-avoiding path problems with the Azure Quantum optimization service

## Introduction

This sample provides a walkthrough on how to solve the self-avoiding path problem with Azure QIO solvers, from problem definition to formulation of constraints to submitting the problem to the Azure QIO Service.

By working through this sample, you will learn:

- Model the problem mathematically to design objective and penalty functions
- Coding of the optimization problem using the Azure Quantum Optimization Python SDK
- Verifying results returned by the solver. 

The work presented in this folder is based on the following [paper - https://arxiv.org/abs/1811.00713](https://arxiv.org/abs/1811.00713). 

## Prerequisites

1. [Create an Azure Quantum Workspace](https://docs.microsoft.com/azure/quantum/how-to-create-quantum-workspaces-with-the-azure-portal)
2. [Install the `azure-quantum` Python module](https://docs.microsoft.com/azure/quantum/optimization-install-sdk)
3. (If you want to run the Jupyter notebook) [Install Jupyter Notebook](https://jupyter.org/install)
4. (Optional / Recommended learning) [Run and understand the basic ship loading sample](../ship-loading/) 

## Running the sample

There are two ways to run the sample (.ipynb and .py):

- [Jupyter Notebook (step-by-step walkthrough)](./self-avoiding-path.ipynb)
- [Python script (barebones annotations)](./self-avoiding-path.py)

A html file of the Jupyter notebook is attached for improved readability:

- [Html page (more readable format than Jupyter Notebook)](./self-avoiding-path.html)

### Running the Jupyter Notebook

To run this sample, use the commandline to navigate to the `self-avoiding-path` folder and run `jupyter notebook`

Your web browser should automatically open a new window.

If this doesn't happen, copy the localhost link shown in the terminal window and paste it into your browser's address bar.

Once you see the page above, simply click on the `self-avoiding-path.ipynb` link to open the sample notebook.

### Running the Python script

- Open up the `self-avoiding-path.py` script using your favorite IDE or a text editor.
- Fill in your Azure Quantum workspace details at the beginning of the script.
- Run the script through your IDE or use the commandline to navigate to the `self-avoiding-path` folder and then run `python ./self-avoiding-path.py` or `python3 ./self-avoiding-path.py` (depending on how your environment is set up).

### Manifest

- **[self-avoiding-path.ipynb](https://github.com/microsoft/qio-samples/blob/main/samples/self-avoiding-path/self-avoiding-path.ipynb)**: Jupyter Notebook version of this sample.
- **[self-avoiding-path.py](https://github.com/microsoft/qio-samples/blob/main/samples/self-avoiding-path/self-avoiding-path.py)**: Standalone Python version of this sample.
- **[self-avoiding-path.html](https://github.com/microsoft/qio-samples/blob/main/samples/self-avoiding-path/self-avoiding-path.html)**: HTML version of this sample.

