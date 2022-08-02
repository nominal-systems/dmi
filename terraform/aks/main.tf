resource "azurerm_kubernetes_cluster" "cluster" {
  name                = "${var.cluster_name}-${var.env_name}"
  resource_group_name = var.rg
  location            = var.location
  dns_prefix          = "${var.cluster_name}-${var.env_name}"

  default_node_pool {
    name       = "default"
    node_count = "2"
    vm_size    = "standard_d2ads_v5"
  }

  identity {
    type = "SystemAssigned"
  }

  tags = {
    Environment = "${var.env_name}"
  }

  http_application_routing_enabled = true
}

resource "azurerm_role_assignment" "ara" {
  principal_id                     = azurerm_kubernetes_cluster.cluster.kubelet_identity[0].object_id
  role_definition_name             = "AcrPull"
  scope                            = var.acr_id
  skip_service_principal_aad_check = true
}
