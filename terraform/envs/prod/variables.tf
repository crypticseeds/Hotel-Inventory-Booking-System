variable "state_bucket" {
  description = "S3 bucket for Terraform state."
  type        = string
}

variable "state_key" {
  description = "Path to the Terraform state file in the bucket."
  type        = string
}

variable "state_region" {
  description = "AWS region for the S3 state bucket."
  type        = string
}

variable "state_lock_table" {
  description = "DynamoDB table for state locking."
  type        = string
} 