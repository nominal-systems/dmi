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
