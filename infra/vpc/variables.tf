variable "azs" {
  type    = list(string)
  default = ["us-east-1a", "us-east-1b"]
}

variable "vpc_name" {
  type    = string
  default = "vpc-test"
}
