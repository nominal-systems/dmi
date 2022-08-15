resource "random_password" "mysql_password" {
  length           = 16
  special          = false
}

resource "azurerm_mysql_server" "mysql_server" {
  name                = "dmi-${var.env_name}-mysqlserver"
  resource_group_name = var.rg
  depends_on          = [random_password.mysql_password]
  location            = var.location

  administrator_login          = var.mysql_username
  administrator_login_password = random_password.mysql_password.result

  sku_name   = "GP_Gen5_2"
  storage_mb = 5120
  version    = "8.0"

  auto_grow_enabled                 = true
  backup_retention_days             = 7
  geo_redundant_backup_enabled      = true
  infrastructure_encryption_enabled = true
  public_network_access_enabled     = var.mysql_public_access
  ssl_enforcement_enabled           = false
  ssl_minimal_tls_version_enforced  = "TLSEnforcementDisabled"
}

resource "azurerm_mysql_firewall_rule" "mysql_firewall_rule" {
  name                = "public-access"
  resource_group_name = var.rg
  depends_on          = [azurerm_mysql_server.mysql_server]
  server_name         = azurerm_mysql_server.mysql_server.name
  start_ip_address    = "0.0.0.0"
  end_ip_address      = "0.0.0.0"
}

resource "azurerm_cosmosdb_account" "cosmosdb_account" {
  name                = "dmi-${var.env_name}-cosmosdb-account"
  resource_group_name = var.rg
  location            = var.location
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
    location          = var.location
  }
}

resource "azurerm_cosmosdb_mongo_database" "mongodb" {
  name                = "dmi-${var.env_name}-cosmos-mongodb"
  resource_group_name = azurerm_cosmosdb_account.cosmosdb_account.resource_group_name
  account_name        = azurerm_cosmosdb_account.cosmosdb_account.name
}

resource "azurerm_redis_cache" "redis" {
  name                = "dmi-${var.env_name}-redis-cache"
  location            = var.location
  resource_group_name = var.rg
  capacity            = 2
  family              = "C"
  sku_name            = "Standard"
  enable_non_ssl_port = true
  minimum_tls_version = "1.2"
}
