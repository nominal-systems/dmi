# Diagnostic Modality Integrator

Base repository for the Diagnostic Modality Integrator (DMI). DMI is a suite of components that connect to diagnostic providers (reference labs, point of care devices, etc) and exposes an API with a single interface for PIMS to implement to integrate with multiple diagnostic providers at once.

In this repository you will find:
- The OpenAPI specification of the DMI API. See [DMI API Specification](spec/README.md).
- A Postman collection to help you started with the API. See [DMI API Postman collection](postman/README.md).
- A set of Docker-related files to help you run the system locally. See [Docker](docker/README.md).
- A set of Kubernetes-related files to help you configure and run the system on a Kubernetes cluster. See [Kubernetes](kubernetes/README.md).
- A set of Terraform-related files to help you provision infrastructure in a cloud provider. See [Terraform](terraform/README.md).
