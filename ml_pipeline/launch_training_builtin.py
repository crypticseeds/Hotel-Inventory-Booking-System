#!/usr/bin/env python3
"""
Launch SageMaker training job with built-in XGBoost (cheaper & faster)
"""
import boto3
import sagemaker
from sagemaker.xgboost import XGBoost

def launch_builtin_xgboost():
    """Use SageMaker's built-in XGBoost algorithm"""
    
    session = sagemaker.Session()
    role = sagemaker.get_execution_role()
    bucket = 'hotel-ml-pipeline-data'
    
    # Built-in XGBoost estimator
    xgb_estimator = XGBoost(
        entry_point='train.py',
        framework_version='1.5-1',
        py_version='py3',
        role=role,
        instance_count=1,
        instance_type='ml.m5.large',
        
        # Cost optimization
        use_spot_instances=True,
        max_wait=3600,
        max_run=1800,
        
        # XGBoost hyperparameters
        hyperparameters={
            'objective': 'reg:squarederror',
            'num_round': 100,
            'max_depth': 6,
            'eta': 0.1,
            'subsample': 0.8,
            'colsample_bytree': 0.8
        }
    )
    
    # Training data
    train_input = f's3://{bucket}/training-data/'
    
    # Start training
    xgb_estimator.fit({'train': train_input})
    
    print(f"Training completed! Model: {xgb_estimator.model_data}")
    return xgb_estimator

if __name__ == "__main__":
    estimator = launch_builtin_xgboost()