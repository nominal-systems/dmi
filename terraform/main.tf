terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "=2.48.0"
    }
  }
}

provider "azurerm" {
  features {}
}

resource "azurerm_resource_group" "rg" {
  name     = "dmi-dev"
  location = "westeurope"
}

resource "azurerm_kubernetes_cluster" "cluster" {
  name                = "dmi-cluster"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  dns_prefix          = "dmi-cluster"

  default_node_pool {
    name       = "default"
    node_count = "2"
    vm_size    = "standard_d2ads_v5"
  }

  identity {
    type = "SystemAssigned"
  }
}
