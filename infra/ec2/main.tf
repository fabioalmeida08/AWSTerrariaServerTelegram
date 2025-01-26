module "ec2_instance" {
  # count  = 1
  source = "terraform-aws-modules/ec2-instance/aws"

  # name = format("instancia_%d", count.index + 1)
  name = "Terraria Server"
  ami  = var.ubuntu_ami

  instance_type          = "t2.micro"
  key_name               = aws_key_pair.tf_keypair.key_name
  monitoring             = false
  vpc_security_group_ids = [var.sg_id]
  subnet_id              = var.subnet_id
  user_data              = file("${path.module}/user_data.sh")
  iam_instance_profile   = var.ec2_instance_profile



  tags = {
    Terraform   = "true"
    Environment = "dev"
  }
}

resource "aws_key_pair" "tf_keypair" {
  key_name   = "tf_keypair"
  public_key = file(var.public_key_path)
}
