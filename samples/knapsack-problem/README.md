---
page_type: sample
languages:
- python
author: benjamintokgoez, alschroe
ms.author: benjamin.tokgz@microsoft.com, alexandra.schroeder@microsoft.com
ms.date: 10/12/2021
products:
- azure-quantum
- azure-qio
description: "Solving the knapsack problem using optimization with the Azure Quantum service"
urlFragment: azure-quantum.knapsack
---

# Solving the knapsack problem using optimization with the Azure Quantum service


## Introduction

This sample provides a comprehensive formulation and implementation of the knapsack problem for solving with optimization solvers and the Azure Quantum service.
The knapsack problem in general solves the following scenario:

Given a knapsack/bag that can hold a finite weight and a number of items with their own weight and a financial value - how can the knapsack/bag be packed so the weight will stay under or be the same as the limit and the financial value of all packed items can be maximized?

This Problem can be applied to optimization tasks where a given limit should not be exceeded and the items hold to values - one to be minimized and one to be maximized.

By working through this sample, you will learn:

- How to transform the given cost function into code using the Azure Quantum Python SDK
- How to submit problem terms to Azure Quantum

## Prerequisites

1. [Create an Azure Quantum Workspace](https://docs.microsoft.com/azure/quantum/how-to-create-quantum-workspaces-with-the-azure-portal)
1. [Install the `azure-quantum` Python module](https://docs.microsoft.com/azure/quantum/optimization-install-sdk)
1. (If you want to run the Jupyter notebook) [Install Jupyter Notebook](https://jupyter.org/install)
1. (Optional) [Run the basic ship loading sample](../ship-loading/)



## Running the sample

There are two ways to run the sample:

- [Jupyter Notebook](./knapsack.ipynb) (with explanations)
- [Python script](/knapsack.py) (barebones annotations)

### Running the Jupyter Notebook

To run this sample, use the command line to navigate to the `knapsack` folder and run 

```shell
jupyter notebook
```

If this does not work try the following:

```shell
python -m notebook
```

Your web browser should automatically open a new window.
If this doesn't happen, copy the localhost link shown in the terminal window and paste it into your browser's address bar.

Once you see the page above, simply click on the knapsack.ipynb link to open the sample notebook.

Here fill in your Azure Quantum workspace details and run all cells.

### Running the Python script

Open up the `knapsack.py` script using your favorite IDE or a text editor.
Fill in your Azure Quantum workspace details at the beginning of the script.
Run the script through your IDE or use the command line to navigate to the `knapsack` folder and then run 

```shell
python ./knapsack.py
```

or

```shell
python3 ./knapsack.py
```

(depending on how your environment is set up).

## Manifest
[knapsack.ipynb](./knapsack.ipynb): Jupyter Notebook version of this sample. <br>
[knapsack.py](/knapsack.py): Standalone Python version of this sample.