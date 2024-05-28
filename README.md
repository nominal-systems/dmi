# Diagnostic Modality Integration API

## Getting Started

### Documentation 
Access the documentation for the Diagnostic Modality Integration API at: https://nominal.stoplight.io/docs/dmi 

### Mock Server
The API has a publicly available mock server that can be used to test and develop integrating into the API: https://stoplight.io/mocks/nominal/dmi/57735574

Alternatively, you can run the mock server locally with [prism](https://meta.stoplight.io/docs/prism/674b27b261c3c-overview):
```bash
npm install -g @stoplight/prism-cli
prism mock reference/dmi.yaml
```
and a mock server will be available at http://127.0.0.1:4010 [^1]

[^1]: When using Postman, ensure that the mock server URL and port match the environment settings.


### Postman Integration
To import the OpenAPI specification file, Postman collections and environments:
1. From your Workspace, click on "Import".
2. Select the "Code repository" tab and click on "GitHub" and follow the GitHub authorization flow.
3. Configure the import:
   1. GitHub organization: nominal-systems
   2. Repository: dmi
   3. Branch: master
4. Review the files to be imported:
   - DMI API (OpenAPI 3.0 API)
   - DMI API Bootstrap (Postman Collection v2.1) 
   - Local (Postman Environment for local environment)
   - Azure Mars VH (Postman Environment for Azure Mars VH environment)
5. Click on "View Import Settings":
   1. On "Parameter generation" select "Schema".
   2. On "Folder organization" select "Tags".
6. Click on "Import"

#### DMI API Bootstrap
Postman collection that includes the following folders:
- Initial Setup: provisions Users, Organizations, Practices, Integrations and Provider Configurations for the Demo Provider
- Events: related to events and event subscriptions.
- Orders & Results: related to ordering tests and getting the order reports.


## Deploy to Azure

### Provision Azure infrastructure with Terraform

Deploy the Terraform stack to Azure:
````
cd terraform
terraform plan
terraform apply
````

This will generate a `kubeconfig-dev` with the Azure Kubernetes Service (AKS) cluster configuration. Configure `kubectl` with:
````
export KUBECONFIG="${PWD}/kubeconfig-dev"
````

To get the Azure Container Registry (ACR) credentials run:
````
az acr credential show -n <ACR_Registry_Name>
````
These credentials must be set as repository secrets for the repositories that need to push images to the registry:
- `REGISTRY_USERNAME` — Username for the registry
- `REGISTRY_PASSWORD` — Either of the passwords for the registry


#### Repository secrets

The following repository secrets must be set in this repository:
- `AZURE_CLIENT_ID` — Azure client/app ID
- `AZURE_CLIENT_SECRET` — Azure client secret/password
- `AZURE_SUBSCRIPTION_ID` — Azure subscription ID
- `AZURE_TENANT_ID` — Azure tenant ID


### Deploy locally to AKS

Deploy the Kubernetes manifests:
````
kubectl apply -f dmi-dev/
````

Get the public IP of the load balancer:
````
kubectl get ingress -o=jsonpath= "-o=jsonpath={.items[0].status.loadBalancer.ingress[0].ip}"
````
