#!/usr/bin/env python3
"""
SageMaker training script for hotel pricing model
"""
import pandas as pd
import numpy as np
import joblib
import argparse
import os
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_absolute_error, r2_score

def preprocess_data(df):
    """Feature engineering for hotel booking data"""
    # Convert date
    df['arrival_date'] = pd.to_datetime(df['arrival_date'], format='%d/%m/%Y')
    df['month'] = df['arrival_date'].dt.month
    df['day_of_week'] = df['arrival_date'].dt.dayofweek
    
    # Encode categoricals
    encoders = {}
    categorical_cols = ['hotel_name', 'room_type', 'market_segment']
    
    for col in categorical_cols:
        le = LabelEncoder()
        df[f'{col}_encoded'] = le.fit_transform(df[col])
        encoders[col] = le
    
    # Convert booleans
    df['is_weekend_num'] = df['is_weekend'].astype(int)
    df['is_holiday_num'] = df['is_holiday'].astype(int)
    
    return df, encoders

def train_model(train_path, model_path):
    """Train pricing model"""
    # Load data
    df = pd.read_csv(os.path.join(train_path, 'bookings.csv'), sep='\t')
    print(f"Loaded {len(df)} records")
    
    # Preprocess
    df, encoders = preprocess_data(df)
    
    # Features
    features = [
        'lead_time', 'stay_length', 'adults', 'children',
        'month', 'day_of_week', 'is_weekend_num', 'is_holiday_num',
        'hotel_name_encoded', 'room_type_encoded', 'market_segment_encoded'
    ]
    
    X = df[features].fillna(0)
    y = df['room_price']
    
    # Split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Train XGBoost
    model = xgb.XGBRegressor(
        n_estimators=100,
        max_depth=6,
        learning_rate=0.1,
        random_state=42,
        n_jobs=-1
    )
    
    model.fit(X_train, y_train)
    
    # Evaluate
    y_pred = model.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    
    print(f"MAE: {mae:.2f}")
    print(f"R2 Score: {r2:.3f}")
    
    # Save model package
    model_package = {
        'model': model,
        'features': features,
        'encoders': encoders,
        'metrics': {'mae': mae, 'r2': r2}
    }
    
    joblib.dump(model_package, os.path.join(model_path, 'model.pkl'))
    print("Model saved successfully")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--model-dir', type=str, default=os.environ.get('SM_MODEL_DIR'))
    parser.add_argument('--train', type=str, default=os.environ.get('SM_CHANNEL_TRAINING'))
    
    args = parser.parse_args()
    train_model(args.train, args.model_dir)