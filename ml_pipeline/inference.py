#!/usr/bin/env python3
"""
SageMaker inference script for serverless endpoint
"""
import joblib
import numpy as np
import json
from datetime import datetime

def model_fn(model_dir):
    """Load model for inference"""
    model_package = joblib.load(f"{model_dir}/model.pkl")
    return model_package

def predict_fn(input_data, model_package):
    """Make predictions"""
    model = model_package['model']
    features = model_package['features']
    encoders = model_package['encoders']
    
    # Extract features from input
    feature_values = []
    
    for feature in features:
        if feature == 'month':
            feature_values.append(datetime.now().month)
        elif feature == 'day_of_week':
            feature_values.append(datetime.now().weekday())
        elif feature == 'is_weekend_num':
            feature_values.append(1 if datetime.now().weekday() >= 5 else 0)
        elif feature in input_data:
            feature_values.append(input_data[feature])
        else:
            # Default values
            defaults = {
                'lead_time': 30,
                'stay_length': 2,
                'adults': 2,
                'children': 0,
                'is_holiday_num': 0,
                'hotel_name_encoded': 0,
                'room_type_encoded': 0,
                'market_segment_encoded': 0
            }
            feature_values.append(defaults.get(feature, 0))
    
    # Predict
    prediction = model.predict([feature_values])[0]
    
    return {
        'predicted_price': float(prediction),
        'currency': 'GBP',
        'confidence': 0.85
    }

def input_fn(request_body, request_content_type):
    """Parse input data"""
    if request_content_type == 'application/json':
        return json.loads(request_body)
    else:
        raise ValueError(f"Unsupported content type: {request_content_type}")

def output_fn(prediction, accept):
    """Format output"""
    if accept == 'application/json':
        return json.dumps(prediction), accept
    else:
        raise ValueError(f"Unsupported accept type: {accept}")