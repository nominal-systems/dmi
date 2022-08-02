resource "local_file" "kubeconfig" {
  filename     = "kubeconfig-${var.env_name}"
  content      = azurerm_kubernetes_cluster.cluster.kube_config_raw
}

output "aks_host" {
  value = azurerm_kubernetes_cluster.cluster.kube_config.0.host
}

output "aks_client_certificate" {
  value = base64decode(azurerm_kubernetes_cluster.cluster.kube_config.0.client_certificate)
}

output "aks_client_key" {
  value = base64decode(azurerm_kubernetes_cluster.cluster.kube_config.0.client_key)
}

output "aks_cluster_ca_certificate" {
  value = base64decode(azurerm_kubernetes_cluster.cluster.kube_config.0.cluster_ca_certificate)
}
