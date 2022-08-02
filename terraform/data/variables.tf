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

variable "mysql_username" {
  description = "Username for the MySQL database"
}

variable "mysql_public_access" {
  description = "Allow public access"
  default = false
}
