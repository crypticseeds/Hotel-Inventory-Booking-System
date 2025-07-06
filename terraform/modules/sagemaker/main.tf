# SageMaker Module Skeleton
resource "aws_sagemaker_notebook_instance" "this" {
  # ... SageMaker notebook instance configuration ...
}

output "notebook_instance_name" {
  value = aws_sagemaker_notebook_instance.this.name
} 