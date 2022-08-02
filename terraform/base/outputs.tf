output "app_rg" {
  value = azurerm_resource_group.rg_app.name
}

output "app_location" {
  value = azurerm_resource_group.rg_app.location
}

output "data_rg" {
  value = azurerm_resource_group.rg_data.name
}

output "data_location" {
  value = azurerm_resource_group.rg_data.location
}
