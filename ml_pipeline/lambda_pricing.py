#!/usr/bin/env python3
"""
Lambda function for pricing API - calls SageMaker endpoint
"""
import json
import boto3
import os
import psycopg2
from datetime import datetime

# Initialize clients
sagemaker_runtime = boto3.client('sagemaker-runtime')

def get_inventory_data(hotel_id, room_type):
    """Get real-time inventory from RDS"""
    try:
        conn = psycopg2.connect(
            host=os.environ['DB_HOST'],
            database=os.environ['DB_NAME'],
            user=os.environ['DB_USER'],
            password=os.environ['DB_PASSWORD']
        )
        
        cursor = conn.cursor()
        cursor.execute("""
            SELECT occupancy_rate, available_rooms 
            FROM inventory 
            WHERE hotel_id = %s AND room_type = %s
        """, (hotel_id, room_type))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'occupancy_rate': result[0],
                'available_rooms': result[1]
            }
    except Exception as e:
        print(f"DB Error: {e}")
    
    # Fallback data
    return {'occupancy_rate': 0.7, 'available_rooms': 10}

def lambda_handler(event, context):
    """Main Lambda handler"""
    try:
        # Parse request
        body = json.loads(event['body']) if 'body' in event else event
        
        # Get inventory data
        inventory = get_inventory_data(
            body.get('hotel_id', 1),
            body.get('room_type', 'Standard')
        )
        
        # Prepare features for SageMaker
        features = {
            'lead_time': body.get('lead_time', 30),
            'stay_length': body.get('stay_length', 2),
            'adults': body.get('adults', 2),
            'children': body.get('children', 0),
            'is_holiday_num': body.get('is_holiday', 0),
            'hotel_name_encoded': body.get('hotel_id', 1) - 1,
            'room_type_encoded': 0,  # Map room types to numbers
            'market_segment_encoded': 1  # Default to online
        }
        
        # Call SageMaker endpoint
        response = sagemaker_runtime.invoke_endpoint(
            EndpointName='hotel-pricing-endpoint',
            ContentType='application/json',
            Body=json.dumps(features)
        )
        
        # Parse response
        result = json.loads(response['Body'].read().decode())
        
        # Apply dynamic pricing based on inventory
        base_price = result['predicted_price']
        occupancy_rate = inventory['occupancy_rate']
        
        # Dynamic pricing logic
        if occupancy_rate > 0.8:
            dynamic_price = base_price * 1.2  # 20% increase
        elif occupancy_rate < 0.5:
            dynamic_price = base_price * 0.9  # 10% discount
        else:
            dynamic_price = base_price
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'room_id': body.get('room_id'),
                'predicted_price': round(dynamic_price, 2),
                'base_price': round(base_price, 2),
                'occupancy_rate': occupancy_rate,
                'available_rooms': inventory['available_rooms'],
                'timestamp': datetime.now().isoformat()
            })
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e),
                'message': 'Pricing prediction failed'
            })
        }