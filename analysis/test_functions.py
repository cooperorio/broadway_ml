# analysis/test_functions.py
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


# VERY crude first test function to see if the webapp code was working.
# NOTE: I think this is vestigial due after finalizing the dashboard
def calculate_basic_metrics(df):
    """
    Calculate basic metrics for the Broadway data.
    This is a test function to verify the dashboard is working.
    """
    results = {}
    
    # Basic metrics
    if 'Grosses ($)' in df.columns:
        results['total_gross'] = df['Grosses ($)'].sum()
        results['avg_gross'] = df['Grosses ($)'].mean()
        results['max_gross'] = df['Grosses ($)'].max()
    
    if 'Attend' in df.columns:
        results['total_attendance'] = df['Attend'].sum()
        results['avg_attendance'] = df['Attend'].mean()
    
    if '% Cap' in df.columns:
        results['avg_capacity'] = df['% Cap'].mean()
    
    # Add some calculated columns
    if 'Grosses ($)' in df.columns and 'Attend' in df.columns:
        df['Revenue_Per_Attendee'] = df['Grosses ($)'] / df['Attend']
        results['avg_revenue_per_attendee'] = df['Revenue_Per_Attendee'].mean()
    
    # Add a simple prediction (this is just a placeholder)
    if 'Grosses ($)' in df.columns:
        # Simple "prediction": next week's gross will be this week's gross ± 10%
        df['Predicted_Gross'] = df['Grosses ($)'] * np.random.uniform(0.9, 1.1, len(df))
        results['prediction_accuracy'] = 0.85  # Placeholder value
    
    return df, results

#####################################################################
## EDAV Course Project Visualizations, translated from R to Python ##
###### (Original project was completed alongside Aylmer Liang) ######
#####################################################################

# Top Grossing Shows Visualization - hold over from when it was a class project
def top_grossing_plot(df):
    """
    Minimalist version - let Plotly handle most formatting
    """
    # Group and aggregate data
    total_gross_data = df.groupby('Show').agg({
        'Grosses ($)': 'sum',
        'Theatre': 'first'
    }).reset_index()
    
    # Get top 40
    total_gross_data = total_gross_data.nlargest(40, 'Grosses ($)')
    
    # Convert to hundred-millions
    total_gross_data['Gross_Hundred_Millions'] = total_gross_data['Grosses ($)'] / 100000000
    
    # Simple scatter plot
    fig = px.scatter(
        total_gross_data,
        x='Gross_Hundred_Millions',
        y='Show',
        color='Theatre',
        title='Top 40 Grossing Broadway Shows',
        labels={
            'Gross_Hundred_Millions': 'Total Gross ($ in Hundred-Millions)',
            'Show': 'Show Name'
        }
    )
    
    # Let Plotly handle most of the layout
    fig.update_layout(
        height=500,
        showlegend=True,
        yaxis={'categoryorder': 'total ascending'}
    )
    
    # Simple hover template
    fig.update_traces(
        hovertemplate='<b>%{y}</b><br>Gross: $%{x:.1f} Hundred Million<extra></extra>'
    )
    
    return fig