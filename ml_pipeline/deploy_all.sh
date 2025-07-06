#!/bin/bash
# Complete ML pipeline deployment script

set -e

echo "🚀 Deploying Hotel ML Pricing Pipeline"

# Step 1: Setup S3 and upload data
echo "📦 Setting up S3 buckets..."
python setup_s3.py

# Step 2: Launch SageMaker training job
echo "🎯 Starting SageMaker training job..."
python launch_training.py

# Wait for training to complete (check AWS console)
echo "⏳ Training job started. Check AWS SageMaker console for completion."
echo "📋 Once training completes, note the model S3 URI and update deploy_endpoint.py"

# Step 3: Deploy serverless endpoint (run after training completes)
echo "🔧 To deploy endpoint after training:"
echo "   1. Update model_uri in deploy_endpoint.py"
echo "   2. Run: python deploy_endpoint.py"

# Step 4: Deploy Lambda function
echo "📡 Deploying Lambda function..."
zip -r lambda_pricing.zip lambda_pricing.py
aws lambda create-function \
    --function-name hotel-pricing-api \
    --runtime python3.9 \
    --role arn:aws:iam::$(aws sts get-caller-identity --query Account --output text):role/lambda-execution-role \
    --handler lambda_pricing.lambda_handler \
    --zip-file fileb://lambda_pricing.zip \
    --timeout 30 \
    --memory-size 512 \
    --environment Variables='{
        "DB_HOST":"your-rds-endpoint",
        "DB_NAME":"hotel_db",
        "DB_USER":"postgres",
        "DB_PASSWORD":"your-password"
    }'

# Step 5: Create API Gateway
echo "🌐 Creating API Gateway..."
aws apigateway create-rest-api --name hotel-pricing-api

echo "✅ Deployment script completed!"
echo "📝 Next steps:"
echo "   1. Complete API Gateway setup in AWS console"
echo "   2. Update PRICING_API_URL in booking service"
echo "   3. Test the integration"