output "vpc_id" {
  value = module.vpc.vpc_id
}

output "eks_cluster_name" {
  value = module.eks.cluster_name
}

output "alb_dns_name" {
  value = module.alb.dns_name
}

output "lambda_function_name" {
  value = module.lambda.function_name
}

output "s3_bucket_name" {
  value = module.s3.bucket_name
}

output "dynamodb_table_name" {
  value = module.dynamodb.table_name
}

output "kms_key_id" {
  value = module.kms.key_id
}

output "secrets_manager_arn" {
  value = module.secrets_manager.arn
}

output "iam_role_arn" {
  value = module.iam.role_arn
}

output "notebook_instance_name" {
  value = module.sagemaker.notebook_instance_name
}

output "rest_api_id" {
  value = module.api_gateway.rest_api_id
}

output "db_instance_endpoint" {
  value = module.rds.db_instance_endpoint
}

output "db_instance_identifier" {
  value = module.rds.db_instance_identifier
} 