# Terraform AWS Production Skeleton

This directory contains a modular, production-grade Terraform setup for deploying core AWS infrastructure for the Hotel Inventory Booking System.

## Structure

```
terraform/
├── modules/           # Reusable infrastructure modules
├── envs/              # Environment-specific configurations (prod only for now)
├── global/            # Provider, backend, and shared config
├── .gitignore         # Ignore sensitive and transient files
└── README.md          # This file
```

## Modules
- **vpc**: Networking (VPC, subnets, NAT, etc.)
- **eks**: Kubernetes cluster for FastAPI services
- **alb**: Application Load Balancer for EKS
- **lambda**: Pricing API (internal only)
- **s3**: S3 buckets (state, assets)
- **dynamodb**: State locking
- **kms**: Encryption keys
- **secrets_manager**: Secrets storage
- **iam**: Roles and policies

## State Management
- S3 bucket for remote state
- DynamoDB for state locking

## DNS
- Use Cloudflare for DNS, pointing to ALB for FastAPI services

## Getting Started
1. Copy `global/providers.tf`, `global/versions.tf`, and `global/terraform.tfvars` as needed.
2. Configure your AWS credentials and Cloudflare API token (if automating DNS).
3. Run `terraform init` in `envs/prod/`.
4. Apply modules as needed.

---

**Note:** This is a skeleton. Fill in module details and variables for your specific use case. 