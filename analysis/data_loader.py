import boto3
import pandas as pd
from io import StringIO

def load_s3_data(bucket_name, file_key):
    """Load CSV data from S3 bucket"""
    s3 = boto3.client('s3')
    response = s3.get_object(Bucket=bucket_name, Key=file_key)
    csv_content = response['Body'].read().decode('utf-8')
    return pd.read_csv(StringIO(csv_content))

def get_s3_file_list(bucket_name, prefix=''):
    """List files in S3 bucket with given prefix"""
    s3 = boto3.client('s3')
    response = s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
    return [obj['Key'] for obj in response.get('Contents', [])]