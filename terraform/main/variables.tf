variable "cluster_name" {
  description = "The name for the AKS cluster"
  default     = "dmi-cluster"
}
variable "env_name" {
  description = "The environment for the AKS cluster"
  default     = "dev"
}

variable "mysql_database" {
  description = "The name of the MySQL"
}

variable "mysql_username" {
  description = "Username for the MySQL database"
}

variable "mysql_public_access" {
  description = "Allow public access"
  default = false
}

variable "demo_provider_database" {
  description = "The name of the Demo Provider Database"
  default     = "demo-provider-api"
}
