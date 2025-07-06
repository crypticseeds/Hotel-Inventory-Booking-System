# DynamoDB Module Skeleton
resource "aws_dynamodb_table" "this" {
  # ... DynamoDB table configuration ...
}

output "table_name" {
  value = aws_dynamodb_table.this.name
} 