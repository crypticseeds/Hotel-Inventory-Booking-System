#!/usr/bin/env python3
"""
Launch SageMaker training job with spot instances
"""
import boto3
import sagemaker
from sagemaker.sklearn import SKLearn
from sagemaker import get_execution_role

def launch_training_job():
    # Setup
    session = sagemaker.Session()
    role = get_execution_role()
    bucket = 'hotel-ml-pipeline-data'
    
    # Training job config
    estimator = SKLearn(
        entry_point='train.py',
        source_dir='.',
        role=role,
        instance_type='ml.m5.large',
        instance_count=1,
        framework_version='1.2-1',
        py_version='py3',
        
        # Cost optimization
        use_spot_instances=True,
        max_wait=3600,  # 1 hour max wait
        max_run=1800,   # 30 min max run
        
        # Hyperparameters
        hyperparameters={
            'n_estimators': 100,
            'max_depth': 10
        }
    )
    
    # Input data
    train_input = f's3://{bucket}/training-data/'
    
    # Start training
    estimator.fit({'training': train_input})
    
    print(f"Training job completed!")
    print(f"Model artifact: {estimator.model_data}")
    
    return estimator

if __name__ == "__main__":
    estimator = launch_training_job()