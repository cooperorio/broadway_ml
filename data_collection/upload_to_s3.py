import boto3
import os
import argparse
from datetime import datetime

def upload_to_s3(bucket_name, file_path, s3_folder="raw"):
    """Uploads a file to S3 using AWS CLI credentials"""
    try:
        # Explicitly use the 'default' profile from AWS CLI config
        # session = boto3.Session(profile_name='default') #redundant since shared credentials
        s3 = boto3.client('s3')
        
        file_name = os.path.basename(file_path)
        timestamp = datetime.now().strftime("%Y%m%d")
        
        # Upload versioned copy
        versioned_path = f"{s3_folder}/versions/{timestamp}_{file_name}"
        s3.upload_file(file_path, bucket_name, versioned_path)
        
        # Update latest reference
        latest_path = f"{s3_folder}/latest/{file_name}"
        s3.upload_file(file_path, bucket_name, latest_path)
        
        print(f"Uploaded to S3:\n- Versioned: s3://{bucket_name}/{versioned_path}")
        print(f"- Latest: s3://{bucket_name}/{latest_path}")
        return True
        
    except Exception as e:
        print(f"Upload failed: {str(e)}")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--bucket", required=True, help="S3 bucket name")
    parser.add_argument("--file", required=True, help="Local CSV file path")
    args = parser.parse_args()
    
    upload_to_s3(args.bucket, args.file)