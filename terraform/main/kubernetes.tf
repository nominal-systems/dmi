provider "kubernetes" {
  host                   = "${azurerm_kubernetes_cluster.cluster.kube_config.0.host}"
  client_certificate     = "${base64decode(azurerm_kubernetes_cluster.cluster.kube_config.0.client_certificate)}"
  client_key             = "${base64decode(azurerm_kubernetes_cluster.cluster.kube_config.0.client_key)}"
  cluster_ca_certificate = "${base64decode(azurerm_kubernetes_cluster.cluster.kube_config.0.cluster_ca_certificate)}"
}

resource "kubernetes_config_map_v1" "dmi-kubernetes_configmap" {
  metadata {
    name = "dmi-config"
  }

  data = {
    DATABASE_HOST           = azurerm_mysql_server.mysql_server.fqdn
    DATABASE_DATABASE       = azurerm_mysql_database.mysql.name
    DATABASE_USERNAME       = "${azurerm_mysql_server.mysql_server.administrator_login}@${azurerm_mysql_server.mysql_server.name}"
    DATABASE_PASSWORD       = azurerm_mysql_server.mysql_server.administrator_login_password
    MONGO_URI               = azurerm_cosmosdb_account.cosmosdb_account.connection_strings[0]
    REDIS_HOST              = azurerm_redis_cache.redis.hostname
    REDIS_PORT              = azurerm_redis_cache.redis.port
    REDIS_PASSWORD          = azurerm_redis_cache.redis.primary_access_key
    DEMO_PROVIDER_DATABASE  = azurerm_mysql_database.demo_provider_mysql.name
  }
}
