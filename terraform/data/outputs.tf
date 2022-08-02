output "mysql_server_name" {
  value = azurerm_mysql_server.mysql_server.name
}

output "mysql_db_host" {
  value = azurerm_mysql_server.mysql_server.fqdn
}

output "mysql_db_username" {
  value = "${azurerm_mysql_server.mysql_server.administrator_login}@${azurerm_mysql_server.mysql_server.name}"
}

output "mysql_db_password" {
  value = azurerm_mysql_server.mysql_server.administrator_login_password
}

output "mongodb_uri" {
  value = azurerm_cosmosdb_account.cosmosdb_account.connection_strings[0]
}

output "redis_host" {
  value = azurerm_redis_cache.redis.hostname
}

output "redis_port" {
  value = azurerm_redis_cache.redis.port
}

output "redis_password" {
  value = azurerm_redis_cache.redis.primary_access_key
}
