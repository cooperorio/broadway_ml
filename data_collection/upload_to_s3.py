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

def upload_latest_csv(bucket_name, csv_path):
    """Uploads the master CSV file to S3 with versioning"""
    s3 = boto3.client('s3')
    file_name = os.path.basename(csv_path)
    
    # Generate versioned filename (YYYYMMDD_broadway_grosses.csv)
    version_prefix = datetime.now().strftime("%Y%m%d")
    s3_key = f"master/{version_prefix}_{file_name}"
    
    # Upload to S3
    s3.upload_file(csv_path, bucket_name, s3_key)
    
    # Also update the "latest" reference file
    s3.upload_file(csv_path, bucket_name, "latest/broadway_grosses.csv")
    
    print(f"Uploaded {file_name} to:")
    print(f"- Versioned: s3://{bucket_name}/{s3_key}")
    print(f"- Latest: s3://{bucket_name}/latest/broadway_grosses.csv")

if __name__ == "__main__":
    check_aws_credentials()
    parser = argparse.ArgumentParser(description='Upload master CSV to S3')
    parser.add_argument('--bucket', required=True, help='S3 bucket name')
    parser.add_argument('--csv', default='broadway_grosses.csv', 
                        help='Path to master CSV file')
    args = parser.parse_args()
    
    upload_latest_csv(args.bucket, args.csv)