output "s3_backup_bucket_id" {
  value = aws_s3_bucket.s3_backup_bucket.id
}

output "s3_backup_bucket_arn" {
  value = aws_s3_bucket.s3_backup_bucket.arn
}