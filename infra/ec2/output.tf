# output "ec2_ips" {
#   value = tolist([for instance in module.ec2_instance : instance.public_ip])
# }

# output "ec2_arns" {
#   value = tolist([for instance in module.ec2_instance : instance.arn])
# }

output "ec2_ips" {
  value = module.ec2_instance.public_ip
}

output "ec2_arns" {
  value = module.ec2_instance.arn
}