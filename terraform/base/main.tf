resource "azurerm_resource_group" "rg_app" {
  name     = "dmi-rg_app-${var.env_name}"
  location = "westeurope"
}

resource "azurerm_resource_group" "rg_data" {
  name     = "dmi-rg_data-${var.env_name}"
  location = "eastus"
}
