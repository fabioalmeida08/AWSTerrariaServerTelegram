variable "ubuntu_ami" {
  type    = string
  default = "ami-0e2c8caa4b6378d8c"
}

# variable "ubuntu_ami" {
#   type    = string
#   default = "ami-09a9858973b288bdd"
# }


variable "sg_id" {
  type = string

}

# variable "subnet_id" {
#   type = string

# }

variable "public_key_path" {
  type = string
}

variable "subnet_id" {
  type = string

}

variable "subnets" {
  description = "List of subnet IDs"
  type        = list(string)
}

variable "ec2_instance_profile" {
  type = string
}