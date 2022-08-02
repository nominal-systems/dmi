variable "env_name" {
  description = "The environment for the AKS cluster"
  default     = "dev"
}

variable "rg" {
  description = "The resource group name for the AKS Cluster"
}

variable "location" {
  description = "The location for the AKS Cluster"
}

variable "cluster_name" {
  description = "The name for the AKS cluster"
  default     = "dmi-cluster"
}

variable "acr_id" {
  description = "The ID of the Azure Container Registry"
}
