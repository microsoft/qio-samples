---
page_type: sample
description: Get started with Microsoft quantum-inspired optimization solvers on Azure Quantum
author: geduardo
ms.author: v-edsanc@microsoft.com
ms.date: 01/25/2021
languages:
- python
products:
- azure-quantum
- azure-qio
---

# Python SDK Basic Sample

This folder has two samples tp demonstrates the basic functionality of the Azure Quantum Python SDK demonstrated in the [Using the Python SDK](https://docs.microsoft.com/azure/quantum/optimization-install-sdk) guide.
The first sample, `microsoft-qio.py` shows how to submit a simple optimization problem. The sample `microsoft-qio-pb.py` shows how to submit a problem with the protobuf input data serialization.

## Prerequisites

To run this sample, please ensure you have [created an Azure Quantum Workspace](https://docs.microsoft.com/azure/quantum/how-to-create-quantum-workspaces-with-the-azure-portal), and followed the [installation steps for the Python SDK](https://docs.microsoft.com/azure/quantum/optimization-install-sdk).

## Running the sample

To run the sample, run:

```bash
python microsoft-qio.py
```

```bash
python microsoft-qio-pb.py
```