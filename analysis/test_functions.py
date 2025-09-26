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

##################################################################
## EDAV Course Project Visualizations, adapted from R to Python ##
###### (Original project completed along side Aylmer Liang) ######
##################################################################

# 1) Top Grossing Shows Visualization
def top_grossing_segmented_bars(df):
    """
    Simplified version using Plotly Express with pre-processed data
    """
    # Group by show and theatre
    show_theatre_gross = df.groupby(['Show', 'Theatre']).agg({
        'Grosses ($)': 'sum',
        'Week End': 'min'
    }).reset_index()
    
    # Calculate total per show for top 40
    show_totals = show_theatre_gross.groupby('Show')['Grosses ($)'].sum().reset_index()
    top_40_shows = show_totals.nlargest(40, 'Grosses ($)')['Show'].tolist()
    
    # Filter and sort
    show_theatre_gross = show_theatre_gross[show_theatre_gross['Show'].isin(top_40_shows)]
    show_theatre_gross = show_theatre_gross.sort_values(['Show', 'Week End'])
    
    # Convert to hundred-millions
    show_theatre_gross['Gross_HM'] = show_theatre_gross['Grosses ($)'] / 100000000
    
    # Create a sequential column for stacking
    show_theatre_gross['Theatre_Order'] = show_theatre_gross.groupby('Show').cumcount()
    
    # Use plotly express with facet (simpler but less control)
    fig = px.bar(
        show_theatre_gross,
        x='Gross_HM',
        y='Show',
        color='Theatre',
        orientation='h',
        title='Top 40 Grossing Broadway Shows - Segmented by Theatre',
        labels={'Gross_HM': 'Total Gross ($ in Hundred-Millions)', 'Show': 'Show Name'},
        category_orders={'Show': top_40_shows[::-1]}  # Reverse to show highest at top
    )
    
    fig.update_layout(
        height=1000,
        barmode='stack',
        yaxis={'categoryorder': 'total ascending'},
        xaxis={'tickformat': '$.1f'},
        legend=dict(
            title='Theatres',
            orientation='v',
            yanchor='top',
            xanchor='left',
            x=1.02,
            y=1
        )
    )
    
    return fig