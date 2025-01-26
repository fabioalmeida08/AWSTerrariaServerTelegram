resource "aws_s3_bucket" "s3_backup_bucket" {
  bucket = "terraria-backup-bucket-${random_string.bucket_suffix.result}"

  tags = {
    Terraform   = "true"
    Environment = "dev"
  }
}


resource "random_string" "bucket_suffix" {
  length  = 8
  special = false
  upper   = false
}