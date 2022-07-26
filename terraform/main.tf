module "dev_cluster" {
  source                = "./main"
  env_name              = "dev"
  cluster_name          = "dmi-cluster"
  mysql_database        = "dmi"
  mysql_username        = "dmi"
  mysql_public_access   = true
}
