# API Gateway Module Skeleton
resource "aws_api_gateway_rest_api" "this" {
  # ... API Gateway REST API configuration ...
}

output "rest_api_id" {
  value = aws_api_gateway_rest_api.this.id
} 