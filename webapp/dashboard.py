import os
import boto3
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from io import StringIO
from dotenv import load_dotenv
from pathlib import Path
import sys
import numpy as np

# Add the parent directory to the path to import from analysis
parent_dir = Path(__file__).parent.parent
sys.path.append(str(parent_dir))

# Try to import analysis functions
try:
    from analysis.test_functions import calculate_basic_metrics
    from analysis.test_functions import top_grossing_plot
    analysis_available = True
except ImportError as e:
    st.warning(f"Analysis module not available: {e}")
    analysis_available = False


# Set page configuration first
st.set_page_config(
    page_title="Exploring Broadway Data",
    page_icon="🎭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load environment variables - now using the correct path
env_path = parent_dir / '.env'
load_dotenv(dotenv_path=env_path)

# Initialize S3 client
@st.cache_resource
def init_s3_client():
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
    
# Load data from S3
@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_s3_data(bucket_name, key):
    try:
        s3 = init_s3_client()
        if s3 is None:
            return None
            
        obj = s3.get_object(Bucket=bucket_name, Key=key)
        df = pd.read_csv(obj['Body'])
        return df
    except Exception as e:
        st.error(f"Error loading data from S3: {e}")
        return None
    
def apply_analysis(df):
    if not analysis_available:
        st.warning("Analysis functions are not available. Using default analysis.")
        # Add some default analysis here
        if 'Grosses ($)' in df.columns and 'Attend' in df.columns:
            df['Gross_Per_Attendee'] = df['Grosses ($)'] / df['Attend']
        return df, {}  # Return empty results dict
    
    try:
        # Use your analysis functions here
        df, results = calculate_basic_metrics(df)
        st.success("Analysis functions applied successfully!")
        return df, results
    except Exception as e:
        st.error(f"Error applying analysis: {e}")
        return df, {}


def main():
    st.title("🎭 Broadway League Data Analysis Dashboard")
    
    # Load data
    with st.spinner("Loading data..."):
        # Replace 'your-bucket-name' with your actual bucket name
        df = load_s3_data('broadway-data-raw', 'raw/latest/broadway_league_data.csv')
    
    if df is None:
        st.error("Failed to load data. Please check your credentials and try again.")
        return
    
    # Apply analysis functions - cursory stuff to prep the data & get basic info
    with st.spinner("Applying analysis..."):
        df, analysis_results = apply_analysis(df)
    
    ############################
    # Front page sidebar stuff #
    ############################

    # Create a copy for filtering
    df_filtered = df.copy()
    
    # Sidebar filters
    st.sidebar.header("Filters")
    
    # Date range filter
    if 'Week End' in df_filtered.columns:
        # Convert to datetime if it's not already
        if not pd.api.types.is_datetime64_any_dtype(df_filtered['Week End']):
            df_filtered['Week End'] = pd.to_datetime(df_filtered['Week End'])
        
        min_date = df_filtered['Week End'].min()
        max_date = df_filtered['Week End'].max()
        
        # Convert to date objects for the date_input widget
        min_date_date = min_date.date()
        max_date_date = max_date.date()
        
        date_range = st.sidebar.date_input(
            "Select Date Range",
            value=(min_date_date, max_date_date),
            min_value=min_date_date,
            max_value=max_date_date
        )
        
        # Apply date filter if two dates are selected
        if len(date_range) == 2:
            start_date, end_date = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
            df_filtered = df_filtered[(df_filtered['Week End'] >= start_date) & 
                                     (df_filtered['Week End'] <= end_date)]
    
    # Show filter
    if 'Show' in df_filtered.columns:
        shows = st.sidebar.multiselect(
            "Select Shows",
            options=df_filtered['Show'].unique(),
            default=df_filtered['Show'].unique()[:5]  # Default to first 5 shows
        )
        df_filtered = df_filtered[df_filtered['Show'].isin(shows)]
    
    # Capacity filter (if available)
    if '% Cap' in df_filtered.columns:
        min_cap, max_cap = st.sidebar.slider(
            "Capacity Range (%)",
            float(df_filtered['% Cap'].min()),
            float(df_filtered['% Cap'].max()),
            (float(df_filtered['% Cap'].min()), float(df_filtered['% Cap'].max()))
        )
        df_filtered = df_filtered[(df_filtered['% Cap'] >= min_cap) & 
                                 (df_filtered['% Cap'] <= max_cap)]
    
    # Main dashboard metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Shows", len(df_filtered['Show'].unique()))
    
    with col2:
        if 'Grosses ($)' in df_filtered.columns:
            st.metric("Total Grosses", f"${df_filtered['Grosses ($)'].sum():,.2f}")
    
    with col3:
        if 'Attend' in df_filtered.columns:
            st.metric("Average Attendance", f"{df_filtered['Attend'].mean():.0f}")
    
    with col4:
        if '% Cap' in df_filtered.columns:
            st.metric("Average Capacity", f"{df_filtered['% Cap'].mean():.1f}%")

    # Analysis Section
    st.subheader("Analysis Results")
    
    if analysis_results:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if 'total_gross' in analysis_results:
                st.metric("Total Gross", f"${analysis_results['total_gross']:,.2f}")
        
        with col2:
            if 'total_attendance' in analysis_results:
                st.metric("Total Attendance", f"{analysis_results['total_attendance']:,.0f}")
        
        with col3:
            if 'avg_capacity' in analysis_results:
                st.metric("Avg Capacity", f"{analysis_results['avg_capacity']:.1f}%")
        
        with col4:
            if 'prediction_accuracy' in analysis_results:
                st.metric("Prediction Accuracy", f"{analysis_results['prediction_accuracy']:.2%}")

    # Visualizations
    st.subheader("Data Visualizations")
    
    # Weekly Grosses Over Time
    if 'Grosses ($)' in df_filtered.columns and 'Week End' in df_filtered.columns:
        fig1 = px.line(df_filtered, x='Week End', y='Grosses ($)', 
                      title='Weekly Grosses Over Time', color='Show' if 'Show' in df_filtered.columns else None)
        st.plotly_chart(fig1, use_container_width=True)
    
    #################################################################################
    # Here is where I add my visualizations adopted from my old class group project #
    #################################################################################

    # Top grossing plot (second - where you want it)
    try:
        fig_top_gross = top_grossing_plot(df_filtered)  # Use filtered data
        st.plotly_chart(fig_top_gross, use_container_width=True)
    except Exception as e:
        st.error(f"Error creating top grossing plot: {e}")
    
    # Show filtered data
    st.subheader("Filtered Data")
    st.dataframe(df_filtered)
    
    # Download button for filtered data
    csv = df_filtered.to_csv(index=False)
    st.download_button(
        label="Download filtered data as CSV",
        data=csv,
        file_name="filtered_broadway_data.csv",
        mime="text/csv"
    )

if __name__ == "__main__":
    main()