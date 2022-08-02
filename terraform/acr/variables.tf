variable "env_name" {
  description = "The environment for the AKS cluster"
  default     = "dev"
}

variable "rg" {
  description = "The resource group name for the ACR Registry"
}

variable "location" {
  description = "The location for the ACR Registry"
}
