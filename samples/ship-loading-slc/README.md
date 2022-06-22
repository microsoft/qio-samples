---
page_type: sample
languages:
- python
author: danielstocker
ms.author: dasto@microsoft.com
ms.date: 09/23/2021
products:
- azure-quantum
- azure-qio
description: "Apply the Slc Term preview to the ship loading sample."
urlFragment: azure-quantum.ship-loading-slc
---

# Ship Loading Sample using squared linear terms for a more efficient formulation

## Introduction

This sample provides a walkthrough of how you can adapt our ship loading sample and make it work with the squared linear combination term type `SlcTerm`. This produces a more efficient problem formulation that will be quicker to upload and faster to process through the solvers that support it. 

Like the original sample this uses Azure Quantum's optimization service.

By working through this sample, you will learn:
- How to introduce the squared linear combination term, `SlcTerm`, in an existing optimization problem
- How to measure the difference in execution speed
- How to compare solution quality between a problem formulation with purely monomial terms and one with grouped terms
- How to submit problem terms to Azure Quantum

## Prerequisites

1. [Create an Azure Quantum Workspace](https://docs.microsoft.com/azure/quantum/how-to-create-quantum-workspaces-with-the-azure-portal)
2. [Install the `azure-quantum` Python module](https://docs.microsoft.com/azure/quantum/optimization-install-sdk)
3. [Install Jupyter Notebook](https://jupyter.org/install)

## Running the sample

There are two ways to run the sample:

- [Jupyter Notebook](./ship-loading-sample-slc.ipynb)
- [Python Script](./ship-loading-sample-slc.py)

### Running the Jupyter Notebook

To run this sample, use the commandline to navigate to the `ship-loading-sample-slc` folder and run `jupyter notebook`.
Once in the UI, simply click the Jupter notebook file to get started. Follow the instructions in the notebook.

### Running the Python script

- Open up the `ship-loading-sample-slc.py` script using your favorite IDE or a text editor.
- Fill in your Azure Quantum workspace details at the beginning of the script.
- Run the script through your IDE or use the commandline to navigate to the folder where you downloaded the script and then run `python ./ship-loading-sample-slc.py` or `python3 ./ship-loading-sample-slc.py` (depending on how your environment is set up).

### Manifest

- **[ship-loading-sample-slc.ipynb](https://github.com/microsoft/qio-samples/blob/main/samples/ship-loading-slc/ship-loading-sample-slc.ipynb)**: Jupyter Notebook version of this sample.
- **[ship-loading-sample-slc.py](https://github.com/microsoft/qio-samples/blob/main/samples/ship-loading-slc/ship-loading-sample-slc.py)**: Standalone Python version of this sample.
