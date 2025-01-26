##############
#  modules   #
##############

module "vpc" {
  source = "./vpc"
}

module "security_group" {
  source = "./sg"
  my_ip  = var.my_ip
  vpc_id = module.vpc.vpc_id
}

module "ec2" {
  source               = "./ec2"
  sg_id                = module.security_group.sg_id
  subnets              = module.vpc.subnet_ids
  ec2_instance_profile = module.iam.ec2_instance_profile
  subnet_id            = module.vpc.subnet_1a
  public_key_path      = var.public_key_path
}

module "ssm" {
  source    = "./ssm"
  token_bot = var.token_bot
}

module "iam" {
  source     = "./iam"
  bucket_arn = module.s3.s3_backup_bucket_arn
}

module "s3" {
  source = "./s3"
}

##############
#  outputs   #
##############

output "ec2s_ip" {
  value = module.ec2.ec2_ips
}
output "ec2s_arn" {
  value = module.ec2.ec2_arns
}
output "bucket_name" {
  value = module.s3.s3_backup_bucket_id
}