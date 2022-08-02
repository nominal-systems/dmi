provider "kubernetes" {
  host                   = var.aks_host
  client_certificate     = var.aks_client_certificate
  client_key             = var.aks_client_key
  cluster_ca_certificate = var.aks_cluster_ca_certificate
}

resource "kubernetes_config_map_v1" "dmi-kubernetes_configmap" {
  metadata {
    name = "dmi-config"
  }

  data = {
    DATABASE_HOST           = var.mysql_db_host
    DATABASE_DATABASE       = azurerm_mysql_database.mysql.name
    DATABASE_USERNAME       = var.mysql_db_username
    DATABASE_PASSWORD       = var.mysql_db_password
    MONGO_URI               = var.mongodb_uri
    REDIS_HOST              = var.redis_host
    REDIS_PORT              = var.redis_port
    REDIS_PASSWORD          = var.redis_password
    DEMO_PROVIDER_DATABASE  = azurerm_mysql_database.demo_provider_mysql.name
  }
}
