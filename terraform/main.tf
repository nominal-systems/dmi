variable "mysql_database" { }

variable "mysql_username" { }

variable "mysql_password" { }

module "dev_cluster" {
  source                = "./main"
  env_name              = "dev"
  cluster_name          = "dmi-cluster"
  mysql_database        = var.mysql_database
  mysql_username        = var.mysql_username
  mysql_password        = var.mysql_password
  mysql_public_access   = true
}
