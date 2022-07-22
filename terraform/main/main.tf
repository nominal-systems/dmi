terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "=3.0.0"
    }
  }
}

provider "azurerm" {
  features {}
}

resource "azurerm_resource_group" "rg" {
  name     = "dmi-rg-${var.env_name}"
  location = "westeurope"
}

resource "azurerm_container_registry" "acr" {
  name                = "nominal${var.env_name}acr"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  sku                 = "Basic"
  admin_enabled       = false
}

resource "azurerm_kubernetes_cluster" "cluster" {
  name                = "${var.cluster_name}-${var.env_name}"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
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
  scope                            = azurerm_container_registry.acr.id
  skip_service_principal_aad_check = true
}
