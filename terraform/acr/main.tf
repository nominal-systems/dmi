resource "azurerm_container_registry" "acr" {
  name                = "nominal${var.env_name}acr"
  resource_group_name = var.rg
  location            = var.location
  sku                 = "Basic"
  admin_enabled       = true
}
