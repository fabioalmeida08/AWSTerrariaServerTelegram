resource "aws_ssm_parameter" "secret" {
  name        = "/Telegram/TokenBot"
  description = "token bot"
  type        = "SecureString"
  value       = var.token_bot
  tier        = "Standard"

  tags = {
    Terraform   = "true"
    Environment = "dev"
  }
}
