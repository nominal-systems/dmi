## Provision Azure Kubernetes Service (AKS) cluster with Terraform

### Configure Azure

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

### Run Terraform

Initialize Terraform:
````
terraform init
````

Build the cluster:
````
terraform plan
terraform apply
````


### Provision Kubernetes

Configure `kubectl`:
````
export KUBECONFIG="${PWD}/kubeconfig-dev"
````

Submit the deployment and load balancer to the AKS cluster:
````
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
kubectl apply -f ingress.yaml
````

Find out the public IP of the load balancer by inspecting the ingress:
````
kubectl describe ingress
````
