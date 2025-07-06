# IAM Module Skeleton
resource "aws_iam_role" "this" {
  # ... IAM role configuration ...
}

output "role_arn" {
  value = aws_iam_role.this.arn
} 