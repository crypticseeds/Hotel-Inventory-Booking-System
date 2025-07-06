# Lambda Module Skeleton
resource "aws_lambda_function" "this" {
  # ... Lambda function configuration ...
}

output "function_name" {
  value = aws_lambda_function.this.function_name
} 