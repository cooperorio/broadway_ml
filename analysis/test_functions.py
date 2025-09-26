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
def top_grossing_plot(df):
    """
    Create a Cleveland dot plot of top 40 grossing shows with proper vertical spacing
    """
    # Group by show and calculate total gross, get first theatre for each show
    total_gross_data = df.groupby('Show').agg({
        'Grosses ($)': 'sum',
        'Theatre': 'first'
    }).reset_index()
    
    # Sort by total gross and take top 40
    total_gross_data = total_gross_data.nlargest(40, 'Grosses ($)')
    
    # Convert to hundred-millions for cleaner x-axis
    total_gross_data['Gross_Hundred_Millions'] = total_gross_data['Grosses ($)'] / 100000000
    
    # Calculate dynamic height based on number of shows (more shows = taller chart)
    base_height = 800  # Base height for good visibility
    min_height = 600   # Minimum height
    max_height = 1200  # Maximum height to prevent excessive scrolling
    
    num_shows = len(total_gross_data)
    dynamic_height = min(max(min_height, base_height + (num_shows - 20) * 15), max_height)
    
    # Create the dot plot
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
    
    # Layout optimized for vertical space
    fig.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white',
        showlegend=True,
        height=dynamic_height,  # Dynamic height based on number of shows
        margin=dict(l=150, r=50, t=80, b=50),  # More left margin for show names
        
        # Title settings
        title={
            'text': 'Top 40 Grossing Broadway Shows',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20},
            'y': 0.98  # Position title near top
        },
        
        # Y-axis settings (critical for show names)
        yaxis={
            'categoryorder': 'total ascending',
            'tickfont': {'size': 12},  # Larger font for readability
            'title': {'text': 'Show Name', 'font': {'size': 14}},
            'automargin': True,  # Let Plotly handle margins for y-axis labels
            'ticksuffix': '  ',  # Add some space after each tick
        },
        
        # X-axis settings
        xaxis={
            'tickformat': '$.1f',
            'title': {'text': 'Total Gross ($ in Hundred-Millions)', 'font': {'size': 14}},
            'tickfont': {'size': 11},
        },
        
        # Legend settings
        legend={
            'title': {'text': 'Theatre', 'font': {'size': 12}},
            'orientation': 'v',
            'yanchor': 'top',
            'xanchor': 'left',
            'x': 1.02,  # Move legend outside the plot area
            'y': 1,
            'bgcolor': 'rgba(255,255,255,0.8)',
            'bordercolor': 'rgba(0,0,0,0.2)',
            'borderwidth': 1
        }
    )
    
    # Marker and hover settings
    fig.update_traces(
        marker=dict(size=8, line=dict(width=1, color='DarkSlateGrey')),
        hovertemplate='<b>%{y}</b><br>Theatre: %{marker.color}<br>Total Gross: $%{x:.1f} Hundred Million<extra></extra>'
    )
    
    return fig