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

# VERY crude first test function to see if the webapp
# code was working.
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

# Top Grossing Shows Visualization - hold over from when it was a class project
def top_grossing_plot(df):
    """
    Create a Cleveland dot plot of top 40 grossing shows, similar to your R visualization
    """
    # Group by show and calculate total gross, get first theatre for each show
    total_gross_data = df.groupby('Show').agg({
        'Grosses ($)': 'sum',
        'Theatre': 'first'  # Assuming you have a 'Theatre' column
    }).reset_index()
    
    # Sort by total gross and take top 40
    total_gross_data = total_gross_data.nlargest(40, 'Grosses ($)')
    
    # Create the Cleveland dot plot (lollipop chart)
    fig = px.scatter(
        total_gross_data,
        x='Grosses ($)',
        y='Show',
        color='Theatre',
        title='Top 40 Grossing Broadway Shows',
        labels={
            'Grosses ($)': 'Total Gross ($ in Hundred-Millions)',
            'Show': 'Show Name'
        }
    )
    
    # Customize the layout to match your R plot
    fig.update_layout(
        # Use a minimal theme
        plot_bgcolor='white',
        paper_bgcolor='white',
        
        # Adjust margins to prevent label cutoff
        margin=dict(l=20, r=10, t=50, b=20),
        
        # Title styling
        title={
            'text': 'Top 40 Grossing Broadway Shows',
            'x': 0.5,  # Center the title
            'xanchor': 'center',
            'font': {'size': 16}
        },
        
        # Y-axis styling (show names)
        yaxis={
            'categoryorder': 'total ascending',  # Sort by gross amount
            'tickfont': {'size': 8}  # Smaller font for show names
        },
        
        # X-axis styling
        xaxis={
            'tickfont': {'size': 9},
            'tickformat': '$,.0f',  # Format as currency
            'title': {'text': 'Total Gross ($ in Hundred-Millions)'}
        },
        
        # Legend styling
        legend={
            'title': 'Initial Theatre',
            'orientation': 'v',  # Vertical legend
            'yanchor': 'top',
            'xanchor': 'left'
        }
    )
    
    # Convert x-axis to hundred-millions (divide by 100,000,000)
    fig.update_xaxes(tickvals=list(range(0, int(total_gross_data['Grosses ($)'].max() // 100000000 + 1) * 100000000, 100000000)),
                    ticktext=[f'${x/100000000:.1f}' for x in range(0, int(total_gross_data['Grosses ($)'].max() // 100000000 + 1) * 100000000, 100000000)])
    
    # Customize the markers
    fig.update_traces(
        marker=dict(size=8, line=dict(width=1, color='DarkSlateGrey')),
        selector=dict(mode='markers')
    )
    
    return fig