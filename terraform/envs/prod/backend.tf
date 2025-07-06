terraform {
  backend "s3" {
    bucket         = var.state_bucket
    key            = var.state_key
    region         = var.state_region
    dynamodb_table = var.state_lock_table
    encrypt        = true
  }
} 