import boto3
import os
import argparse
from datetime import datetime

# Add to top of upload_to_s3.py
def check_aws_credentials():
    if not os.getenv('AWS_ACCESS_KEY_ID') or not os.getenv('AWS_SECRET_ACCESS_KEY'):
        print("AWS credentials not configured!")
        print("Run 'aws configure' or set environment variables")
        exit(1)

def upload_to_s3(bucket_name, file_path, s3_folder="raw"):
    """Uploads a file to S3 with versioning"""
    s3 = boto3.client('s3')
    file_name = os.path.basename(file_path)
    
    # Create versioned filename (YYYYMMDD_filename.csv)
    timestamp = datetime.now().strftime("%Y%m%d")
    versioned_name = f"{timestamp}_{file_name}"
    
    # Upload paths
    versioned_path = f"{s3_folder}/versions/{versioned_name}"
    latest_path = f"{s3_folder}/latest/{file_name}"
    
    try:
        # Upload versioned copy
        s3.upload_file(file_path, bucket_name, versioned_path)
        
        # Update latest reference
        s3.upload_file(file_path, bucket_name, latest_path)
        
        print(f"Uploaded to S3:")
        print(f"- Versioned: s3://{bucket_name}/{versioned_path}")
        print(f"- Latest: s3://{bucket_name}/{latest_path}")
        return True
    except Exception as e:
        print(f"Upload failed: {str(e)}")
        return False

if __name__ == "__main__":
    check_aws_credentials()
    parser = argparse.ArgumentParser()
    parser.add_argument("--bucket", required=True, help="S3 bucket name")
    parser.add_argument("--file", required=True, help="Local CSV file path")
    args = parser.parse_args()
    
    upload_to_s3(args.bucket, args.file)