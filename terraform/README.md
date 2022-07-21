## Provision Azure Kubernetes Service (AKS) cluster

### Azure CLI

Login to Azure:
````
az login
````

Create a [resource group](https://docs.microsoft.com/en-us/azure/azure-resource-manager/management/manage-resource-groups-cli#what-is-a-resource-group):
````
az group create --name dmi-dev --location westeurope
````

Register a [resource provider](https://docs.microsoft.com/en-us/azure/azure-resource-manager/management/resource-providers-and-types) for AKS:
````
az provider register -n Microsoft.ContainerService
````

Create the AKS cluster:
```` 
az aks create -n dmi-dev -g dmi-dev -s standard_d2ads_v5 --generate-ssh-keys --node-count 2  
````

Get the cluster details:
````
az aks show --name dmi-dev --resource-group dmi-dev -o yaml
````

Fetch the credentials for k8s:
````
az aks get-credentials --resource-group dmi-dev --name dmi-dev
````

Verify that you can access the AKS cluster with `kubectl`:
````
kubectl get nodes
````

### Terraform

Get the Subscription ID:
````
az account list
````

Terraform needs a Service Principal to create resources on your behalf. 

Create the Service Principal:
````
az ad sp create-for-rbac \
  --role="Contributor" \
  --scopes="/subscriptions/SUBSCRIPTION_ID"
````
where `SUBSCRIPTION_ID` is the Subscription ID.

This will output a JSON like:
````json
{
  "appId": "00000000-0000-0000-0000-000000000000",
  "displayName": "azure-cli-2021-02-13-20-01-37",
  "name": "http://azure-cli-2021-02-13-20-01-37",
  "password": "0000-0000-0000-0000-000000000000",
  "tenant": "00000000-0000-0000-0000-000000000000"
}
````

Export the following environment variables:
````
export ARM_CLIENT_ID=<insert the appId from above>
export ARM_SUBSCRIPTION_ID=<insert your subscription id>
export ARM_TENANT_ID=<insert the tenant from above>
export ARM_CLIENT_SECRET=<insert the password from above>
````

Initialize Terraform:
````
terraform init
````

Build the cluster:
````
terraform plan
terraform apply
````

Inspect the cluster using the created `kubeconfig` file:
````
kubectl get node --kubeconfig kubeconfig
````

Optionally, export `KUBECONFIG` to avoid using the `kubeconfig` flag:
````
export KUBECONFIG="${PWD}/kubeconfig"
kubectl get node
````
