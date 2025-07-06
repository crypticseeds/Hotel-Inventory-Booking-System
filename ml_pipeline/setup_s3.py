#!/usr/bin/env python3
"""
Setup S3 buckets and upload training data
Supports: Local files, RDS export, or manual upload
"""
import boto3
import os
import pandas as pd
import psycopg2

def create_s3_bucket():
    """Create S3 bucket for ML data"""
    s3 = boto3.client('s3')
    bucket_name = 'hotel-ml-pipeline-data'
    
    try:
        # Handle different AWS regions
        region = boto3.Session().region_name
        if region == 'us-east-1':
            s3.create_bucket(Bucket=bucket_name)
        else:
            s3.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration={'LocationConstraint': region}
            )
        print(f"✅ Created bucket: {bucket_name}")
        return bucket_name
    except Exception as e:
        if "BucketAlreadyExists" in str(e) or "BucketAlreadyOwnedByYou" in str(e):
            print(f"✅ Bucket already exists: {bucket_name}")
            return bucket_name
        print(f"❌ Error creating bucket: {e}")
        return None

def upload_local_files(bucket_name):
    """Option 1: Upload local CSV files"""
    s3 = boto3.client('s3')
    
    files_to_upload = [
        ('synthetic_hotel_bookings_2024_2025.csv', 'training-data/bookings.csv'),
        ('inventory_data.csv', 'training-data/inventory.csv')
    ]
    
    for local_file, s3_key in files_to_upload:
        if os.path.exists(local_file):
            s3.upload_file(local_file, bucket_name, s3_key)
            print(f"✅ Uploaded {local_file} to s3://{bucket_name}/{s3_key}")
        else:
            print(f"⚠️  File not found: {local_file}")

def export_from_rds(bucket_name):
    """Option 2: Export data directly from RDS"""
    try:
        # Connect to RDS
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            database=os.getenv('DB_NAME', 'hotel_db'),
            user=os.getenv('DB_USER', 'postgres'),
            password=os.getenv('DB_PASSWORD')
        )
        
        # Export bookings data
        bookings_query = """
        SELECT booking_id, hotel_id, arrival_date, lead_time, stay_length,
               adults, children, room_type, market_segment, is_weekend,
               is_holiday, room_price, reservation_status
        FROM bookings 
        WHERE reservation_status IN ('confirmed', 'checked-out')
        """
        
        bookings_df = pd.read_sql(bookings_query, conn)
        
        # Export inventory data
        inventory_query = """
        SELECT hotel_id, room_type, date, available_rooms, 
               total_rooms, occupancy_rate
        FROM inventory
        WHERE date >= CURRENT_DATE - INTERVAL '365 days'
        """
        
        inventory_df = pd.read_sql(inventory_query, conn)
        conn.close()
        
        # Save to S3
        s3 = boto3.client('s3')
        
        # Upload bookings
        bookings_csv = bookings_df.to_csv(index=False)
        s3.put_object(
            Bucket=bucket_name,
            Key='training-data/bookings_from_rds.csv',
            Body=bookings_csv.encode('utf-8')
        )
        
        # Upload inventory
        inventory_csv = inventory_df.to_csv(index=False)
        s3.put_object(
            Bucket=bucket_name,
            Key='training-data/inventory_from_rds.csv',
            Body=inventory_csv.encode('utf-8')
        )
        
        print(f"✅ Exported {len(bookings_df)} bookings from RDS")
        print(f"✅ Exported {len(inventory_df)} inventory records from RDS")
        
    except Exception as e:
        print(f"❌ RDS export failed: {e}")
        print("💡 Make sure DB environment variables are set")

def setup_s3_data(method='local'):
    """Main setup function"""
    print(f"🚀 Setting up S3 data using method: {method}")
    
    # Create bucket
    bucket_name = create_s3_bucket()
    if not bucket_name:
        return None
    
    # Upload data based on method
    if method == 'local':
        print("📁 Uploading local CSV files...")
        upload_local_files(bucket_name)
        
    elif method == 'rds':
        print("🗄️  Exporting data from RDS...")
        export_from_rds(bucket_name)
        
    elif method == 'manual':
        print("📋 Manual upload instructions:")
        print(f"   1. Go to AWS S3 Console")
        print(f"   2. Navigate to bucket: {bucket_name}")
        print(f"   3. Create folder: training-data/")
        print(f"   4. Upload your CSV files to training-data/")
        
    return bucket_name

if __name__ == "__main__":
    import sys
    
    # Choose method: local, rds, or manual
    method = sys.argv[1] if len(sys.argv) > 1 else 'local'
    
    print("🎯 Hotel ML Pipeline - S3 Setup")
    print("Available methods:")
    print("  local  - Upload local CSV files")
    print("  rds    - Export directly from RDS")
    print("  manual - Instructions for manual upload")
    print()
    
    setup_s3_data(method)