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
  admin_enabled       = true
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

resource "azurerm_mysql_server" "mysql_server" {
  name                = "dmi-${var.env_name}-mysqlserver"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name

  administrator_login          = var.mysql_username
  administrator_login_password = var.mysql_password

  sku_name   = "GP_Gen5_2"
  storage_mb = 5120
  version    = "8.0"

  auto_grow_enabled                 = true
  backup_retention_days             = 7
  geo_redundant_backup_enabled      = true
  infrastructure_encryption_enabled = true
  public_network_access_enabled     = var.mysql_public_access
  ssl_enforcement_enabled           = false
  ssl_minimal_tls_version_enforced  = "TLS1_2"
}

resource "azurerm_mysql_database" "mysql" {
  name                = var.mysql_database
  resource_group_name = azurerm_resource_group.rg.name
  server_name         = azurerm_mysql_server.mysql_server.name
  charset             = "utf8"
  collation           = "utf8_unicode_ci"
}

resource "azurerm_mysql_firewall_rule" "mysql_firewall_rule" {
  name                = "public-access"
  resource_group_name = azurerm_resource_group.rg.name
  server_name         = azurerm_mysql_server.mysql_server.name
  start_ip_address    = "0.0.0.0"
  end_ip_address      = "0.0.0.0"
}

resource "azurerm_resource_group" "rg_data" {
  name     = "dmi-rg_data-${var.env_name}"
  location = "eastus"
}

resource "azurerm_cosmosdb_account" "cosmosdb_account" {
  name                = "dmi-${var.env_name}-cosmosdb-account"
  resource_group_name = azurerm_resource_group.rg_data.name
  location            = azurerm_resource_group.rg_data.location
  offer_type          = "Standard"
  kind                = "MongoDB"
  enable_free_tier    = true
  capabilities {
    name                    = "MongoDBv3.4"
  }
  capabilities {
    name                    = "EnableMongo"
  }
  consistency_policy {
    consistency_level       = "Session"
  }
  geo_location {
    failover_priority = 0
    location          = azurerm_resource_group.rg_data.location
  }
}

resource "azurerm_cosmosdb_mongo_database" "mongodb" {
  name                = "dmi-${var.env_name}-cosmos-mongodb"
  resource_group_name = azurerm_cosmosdb_account.cosmosdb_account.resource_group_name
  account_name        = azurerm_cosmosdb_account.cosmosdb_account.name
}

resource "azurerm_servicebus_namespace" "activemq" {
  name                = "dmi-${var.env_name}-servicebus-namespace"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  sku                 = "Standard"
}
