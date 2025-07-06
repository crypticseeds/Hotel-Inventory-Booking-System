#!/usr/bin/env python3
"""
Deploy model to SageMaker Serverless Endpoint
"""
import boto3
import sagemaker
from sagemaker.sklearn import SKLearnModel
from sagemaker.serverless import ServerlessInferenceConfig

def deploy_serverless_endpoint(model_data_uri):
    """Deploy trained model to serverless endpoint"""
    
    # Setup
    session = sagemaker.Session()
    role = sagemaker.get_execution_role()
    
    # Create model
    model = SKLearnModel(
        model_data=model_data_uri,
        role=role,
        entry_point='inference.py',
        source_dir='.',
        framework_version='1.2-1',
        py_version='py3'
    )
    
    # Serverless config
    serverless_config = ServerlessInferenceConfig(
        memory_size_in_mb=1024,
        max_concurrency=5
    )
    
    # Deploy
    predictor = model.deploy(
        serverless_inference_config=serverless_config,
        endpoint_name='hotel-pricing-endpoint'
    )
    
    print(f"Endpoint deployed: {predictor.endpoint_name}")
    return predictor

if __name__ == "__main__":
    # Replace with your model S3 URI from training job
    model_uri = "s3://hotel-ml-pipeline-data/model/model.tar.gz"
    deploy_serverless_endpoint(model_uri)