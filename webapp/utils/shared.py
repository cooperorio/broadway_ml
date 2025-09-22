# webapp/utils/shared.py
import os
import boto3
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from pathlib import Path
import sys

# Add parent directory to path
parent_dir = Path(__file__).parent.parent.parent
sys.path.append(str(parent_dir))

# Load environment variables
env_path = parent_dir / '.env'
load_dotenv(dotenv_path=env_path)

@st.cache_resource
def init_s3_client():
    """Initialize S3 client (cached)"""
    try:
        session = boto3.Session(
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('AWS_DEFAULT_REGION', 'us-east-1')
        )
        return session.client('s3')
    except Exception as e:
        st.error(f"Error initializing S3 client: {e}")
        return None

@st.cache_data(ttl=3600)
def load_data():
    """Load data from S3 (cached for 1 hour)"""
    try:
        s3 = init_s3_client()
        if s3 is None:
            return None
            
        # Replace with your actual bucket and key
        obj = s3.get_object(Bucket='broadway-data-raw', Key='raw/latest/broadway_league_data.csv')
        df = pd.read_csv(obj['Body'])
        
        # Convert date columns
        if 'Week End' in df.columns:
            df['Week End'] = pd.to_datetime(df['Week End'])
            
        return df
    except Exception as e:
        st.error(f"Error loading data from S3: {e}")
        return None

def get_data():
    """Get data, using session state to avoid reloading"""
    if 'df' not in st.session_state:
        with st.spinner("Loading data..."):
            st.session_state.df = load_data()
    return st.session_state.df