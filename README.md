# Azure Quantum optimization service samples

These samples demonstrate the use of the Azure Quantum QIO service.

Each sample is self-contained in a folder, and demonstrates how to use the QIO service to solve a problem.

## Prerequisites

To run these samples, there are some prerequisites:

1. [Create an Azure Quantum Workspace](https://docs.microsoft.com/azure/quantum/how-to-create-quantum-workspaces-with-the-azure-portal)
1. [Install Python on your system](https://www.python.org/downloads/)
1. [Install the `azure-quantum` Python module](https://docs.microsoft.com/azure/quantum/how-to-use-the-python-sdk)
1. (Optional) [Install Jupyter Notebook](https://jupyter.org/install)

## Getting Started

If you're new to the Azure Quantum QIO service, we recommend starting with the [Getting Started samples](./samples/getting-started/), which run through how to set up and submit problems to be solved using the service.

After that, we recommend exploring the other samples in this repository, which demonstrate the use of the Azure Quantum QIO service to solve specific optimization problems. We recommend that you use the Jupyter Notebook versions of these samples if you are new to the QIO service as they contain detailed, step-by-step instructions on how to formulate and solve the problem instance.

We recommend starting with the [ship loading sample](./samples/ship-loading/) before moving on to the [job shop scheduling sample](./samples/job-shop-scheduling), as job shop scheduling introduces some more complex ideas, so it is useful to understand the basics of problem formulation first. Both of these problems have associated Microsoft Learn modules which you can find here:

- [Ship loading](https://docs.microsoft.com/learn/modules/solve-quantum-inspired-optimization-problems/)
- [Job shop scheduling](https://docs.microsoft.com/learn/modules/solve-job-shop-optimization-azure-quantum/)

## List of Available Samples

- [Getting Started](./samples/getting-started/)
  - [1QBit](./samples/getting-started/1qbit)
  - [Microsoft QIO](./samples/getting-started/microsoft-qio)
- [Ship Loading Sample](./samples/ship-loading/)
- [Job Shop Scheduling Sample](./samples/job-shop-scheduling)

## Contributing

This project welcomes contributions and suggestions.  Most contributions require you to agree to a
Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us
the rights to use your contribution. For details, visit https://cla.opensource.microsoft.com.

When you submit a pull request, a CLA bot will automatically determine whether you need to provide
a CLA and decorate the PR appropriately (e.g., status check, comment). Simply follow the instructions
provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).
For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or
contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.

## Trademarks

This project may contain trademarks or logos for projects, products, or services. Authorized use of Microsoft
trademarks or logos is subject to and must follow
[Microsoft's Trademark & Brand Guidelines](https://www.microsoft.com/legal/intellectualproperty/trademarks/usage/general).
Use of Microsoft trademarks or logos in modified versions of this project must not cause confusion or imply Microsoft sponsorship.
Any use of third-party trademarks or logos are subject to those third-party's policies.
