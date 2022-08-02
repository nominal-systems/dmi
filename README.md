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
and a mock server will be available at http://127.0.0.1:4010

### Postman integration
To import the OpenAPI specification file, Postman collections and environments:
1. From your Workspace, click on "Import".
2. Select the "Code repository" tab and click on "GitHub" and follow the GitHub authorization flow.
3. Configure the import:
   1. GitHub organization: nominal-systems
   2. Repository: dmi
   3. Branch: master
4. Review the files to be imported:
   - DMI API (OpenAPI 3.0 API)
   - DMI API [Local] (Postman environment for local server)
   - DMI API [Mock Server] (Postman environment for remote mock server)
5. Click on "Show advanced settings":
   1. On "Request parameter generation" select "Schema".
   2. On "Folder organization" select "Tags".
6. Click on "Import"

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


### Deploy to AKS

Deploy the Kubernetes manifests:
````
kubectl apply -f dmi-dev/
````

Get the public IP of the load balancer:
````
kubectl get ingress -o=jsonpath= "-o=jsonpath={.items[0].status.loadBalancer.ingress[0].ip}"
````
