module "sg" {
  source = "terraform-aws-modules/security-group/aws"

  name        = "teste_sg"
  description = "Security group for test with ssh enable "
  vpc_id      = var.vpc_id

  # ingress_cidr_blocks = ["0.0.0.0/0"]
  # ingress_rules       = ["http-80-tcp"]

  ingress_with_cidr_blocks = [
    {
      from_port   = 7777
      to_port     = 7777
      protocol    = "tcp"
      description = "terraria port tcp"
      cidr_blocks = "0.0.0.0/0"
    },
    {
      from_port   = 7777
      to_port     = 7777
      protocol    = "udp"
      description = "terraria port udp"
      cidr_blocks = "0.0.0.0/0"
    },
    {
      from_port   = 22
      to_port     = 22
      protocol    = "tcp"
      description = "ssh port"
      cidr_blocks = var.my_ip
    },
  ]

  ingress_with_ipv6_cidr_blocks = [
    {
      from_port        = 7777
      to_port          = 7777
      protocol         = "tcp"
      description      = "terraria port tcp"
      ipv6_cidr_blocks = "::/0" 
    },
    {
      from_port        = 7777
      to_port          = 7777
      protocol         = "udp"
      description      = "terraria port udp"
      ipv6_cidr_blocks = "::/0"              
    },
  ]

  egress_with_cidr_blocks = [
    {
      from_port   = 0
      to_port     = 0
      protocol    = "-1"
      description = "all traffic"
      cidr_blocks = "0.0.0.0/0"
    }
  ]

  egress_with_ipv6_cidr_blocks = [
    {
      from_port        = 0
      to_port          = 0
      protocol         = "-1"
      description      = "User-service ports (ipv6)"
      ipv6_cidr_blocks = "::/0"
    }
  ]

  tags = {
    Terraform   = "true"
    Environment = "dev"
  }
}