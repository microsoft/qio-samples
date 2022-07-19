---
page_type: sample
languages:
- python
author: delbert murphy
ms.author: delbertm@microsoft.com
products:
- azure-qio
- azure-quantum
description: "Learn how to represent a Secret Santa draw as a binary problem and solve it using the Azure Quantum service"
urlFragment: azure-quantum.secret-santa
---

# Solving the Secret Santa scenario with optimization solvers and the Azure Quantum service

## Introduction

This sample provides a simple example of how to solve an optimization problem using Azure Quantum. In the example, three friends Vincent, Tess, and Uma participate in a Secret Santa draw by writing their names on slips of paper and placing them in a jar. Then, each draws a slip of paper at random and buys a small gift and writes a poem for the person whose name they drew. We will automate this process.

This amounts to a binary satisfiability problem, as outlined in the Jupyter Notebook for this sample.

## Prerequisites

1. [Create an Azure Quantum Workspace](https://docs.microsoft.com/azure/quantum/optimization-install-sdk)
2. [Install the `azure-quantum` Python module](https://docs.microsoft.com/azure/quantum/optimization-install-sdk)
3. (If you want to run the Jupyter notebook) [Install Jupyter Notebook](https://jupyter.org/install)

## Running the sample

There are two ways to run the sample:

- Jupyter Notebook (full sample walkthrough)
- Python script (just the code)

### Running the Jupyter Notebook

To run this sample, use the command line to navigate to the `secret-santa` folder and run `jupyter notebook`.

Your web browser should automatically open a new window showing something similar to the below:

![Jupyter Notebook landing page](./media/jupyter-homepage.png)

If this doesn't happen, copy the localhost link shown in the terminal window and paste it into your browser's address bar.

Once you see the page above, simply click on the `secret-santa.ipynb` link to open the sample notebook.

### Running the Python script

- Open up the `secret-santa.py` script using your favorite IDE or a text editor.
- Fill in your Azure Quantum workspace details at the beginning of the script.
- Run the script through your IDE or use the command line to navigate to the `secret-santa` folder and then run `python ./secret-santa.py` or `python3 ./secret-santa.py` (depending on how your environment is set up).

## Manifest

- **[secret-santa.ipynb](https://github.com/microsoft/qio-samples/blob/main/samples/secret-santa/secret-santa.ipynb)**: Jupyter Notebook version of this sample.
- **[secret-santa.py](https://github.com/microsoft/qio-samples/blob/main/samples/secret-santa/secret-santa.py)**: Standalone Python version of this sample.
