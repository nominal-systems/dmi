# Kubernetes

## Run locally

Start your Kubernetes cluster using `minikube`:
````
minikube start
minikube status
````

Submit the resource definitions to Kubernetes:
````
kubectl apply -f local
````

Get the URL of the DMI API by running:
````
minikube service dmi-api --url
````


## Run in Azure
Inspect the cluster using the created `kubeconfig` file:
````
kubectl get node --kubeconfig kubeconfig
````

Optionally, export `KUBECONFIG` to avoid using the `kubeconfig` flag:
````
export KUBECONFIG="${PWD}/kubeconfig"
kubectl get node
````

Submit the deployment and load balancer to the AKS cluster:
````
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
kubectl apply -f ingress.yaml
````

Get the public IP of the load balancer:
````
kubectl get svc
````
