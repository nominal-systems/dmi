resource "azurerm_mysql_database" "mysql" {
  name                = var.dmi_api_database
  resource_group_name = var.rg
  server_name         = var.mysql_server
  charset             = "utf8"
  collation           = "utf8_unicode_ci"
}

resource "azurerm_mysql_database" "demo_provider_mysql" {
  name                = var.demo_provider_database
  resource_group_name = var.rg
  server_name         = var.mysql_server
  charset             = "utf8"
  collation           = "utf8_unicode_ci"
}
