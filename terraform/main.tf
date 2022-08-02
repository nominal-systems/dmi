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

module "base" {
  source                      = "./base"
  env_name                    = "dev"
}

module "acr_registry" {
  source                      = "./acr"
  rg                          = module.base.data_rg
  location                    = module.base.data_location
}

module "aks_cluster" {
  source                      = "./aks"
  env_name                    = "dev"
  cluster_name                = "dmi-cluster"
  rg                          = module.base.app_rg
  location                    = module.base.app_location
  acr_id                      = module.acr_registry.id
}

module "data" {
  source                      = "./data"
  env_name                    = "dev"
  rg                          = module.base.data_rg
  location                    = module.base.data_location
  mysql_username              = "dmi"
  mysql_public_access         = true
}

module "main" {
  source                      = "./main"
  env_name                    = "dev"
  rg                          = module.base.data_rg
  location                    = module.base.data_location
  aks_host                    = module.aks_cluster.aks_host
  aks_client_certificate      = module.aks_cluster.aks_client_certificate
  aks_client_key              = module.aks_cluster.aks_client_key
  aks_cluster_ca_certificate  = module.aks_cluster.aks_cluster_ca_certificate
  mysql_server                = module.data.mysql_server_name
  mysql_db_host               = module.data.mysql_db_host
  mysql_db_username           = module.data.mysql_db_username
  mysql_db_password           = module.data.mysql_db_password
  mongodb_uri                 = module.data.mongodb_uri
  redis_host                  = module.data.redis_host
  redis_port                  = module.data.redis_port
  redis_password              = module.data.redis_password
  dmi_api_database            = "dmi"
  demo_provider_database      = "demo-provider-api"
}
