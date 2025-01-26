output "igw_id" {
  value = module.vpc.igw_id
}
output "public_subnets" {
  value = module.vpc.public_subnets
}

output "vpc_id" {
  value = module.vpc.vpc_id
}

output "subnet_ids" {
  value = module.vpc.public_subnets
}

output "subnet_1a" {
  value = module.vpc.public_subnets[0]
}