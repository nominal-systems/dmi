variable "env_name" {
  description = "The environment for the AKS cluster"
  default     = "dev"
}

variable "rg" {
  description = "The resource group name for the resources"
}

variable "location" {
  description = "The location for the resources"
}

variable "aks_host" {}
variable "aks_client_certificate" {}
variable "aks_client_key" {}
variable "aks_cluster_ca_certificate" {}
variable "mysql_server" {}
variable "mysql_db_host" {}
variable "mysql_db_username" {}
variable "mysql_db_password" {}
variable "mongodb_uri" {}
variable "redis_host" {}
variable "redis_port" {}
variable "redis_password" {}

variable "dmi_api_database" {
  description = "The name of the MySQL"
  default     = "dmi"
}

variable "demo_provider_database" {
  description = "The name of the Demo Provider Database"
  default     = "demo-provider-api"
}
