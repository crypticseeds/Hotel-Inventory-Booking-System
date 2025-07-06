module "vpc" {
  source = "../../modules/vpc"
  # Add VPC variables here
}

module "eks" {
  source = "../../modules/eks"
  # Add EKS variables here
}

module "alb" {
  source = "../../modules/alb"
  # Add ALB variables here
}

module "lambda" {
  source = "../../modules/lambda"
  # Add Lambda variables here
}

module "s3" {
  source = "../../modules/s3"
  # Add S3 variables here
}

module "dynamodb" {
  source = "../../modules/dynamodb"
  # Add DynamoDB variables here
}

module "kms" {
  source = "../../modules/kms"
  # Add KMS variables here
}

module "secrets_manager" {
  source = "../../modules/secrets_manager"
  # Add Secrets Manager variables here
}

module "iam" {
  source = "../../modules/iam"
  # Add IAM variables here
} 