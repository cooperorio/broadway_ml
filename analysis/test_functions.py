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
    Create a horizontal bar chart where each show's bar is segmented by theatres,
    with segments proportional to the gross revenue from each theatre.
    """
    # Group by show and theatre to get total gross per show-theatre combination
    show_theatre_gross = df.groupby(['Show', 'Theatre']).agg({
        'Grosses ($)': 'sum',
        'Week End': ['min', 'max']  # Get first and last week for chronology
    }).reset_index()
    
    # Flatten the column names
    show_theatre_gross.columns = ['Show', 'Theatre', 'Total_Gross', 'First_Week', 'Last_Week']
    
    # Calculate total gross per show for sorting
    show_totals = show_theatre_gross.groupby('Show')['Total_Gross'].sum().reset_index()
    top_40_shows = show_totals.nlargest(40, 'Total_Gross')['Show'].tolist()
    
    # Filter to only top 40 shows
    show_theatre_gross = show_theatre_gross[show_theatre_gross['Show'].isin(top_40_shows)]
    
    # Sort theatres within each show by first week (chronological order)
    show_theatre_gross = show_theatre_gross.sort_values(['Show', 'First_Week'])
    
    # Calculate cumulative gross for each show (for segment positioning)
    show_theatre_gross['Cumulative_Gross'] = show_theatre_gross.groupby('Show')['Total_Gross'].cumsum()
    show_theatre_gross['Segment_Start'] = show_theatre_gross.groupby('Show')['Cumulative_Gross'].shift().fillna(0)
    
    # Convert to hundred-millions for better axis formatting
    show_theatre_gross['Total_Gross_HM'] = show_theatre_gross['Total_Gross'] / 100000000
    show_theatre_gross['Segment_Start_HM'] = show_theatre_gross['Segment_Start'] / 100000000
    show_theatre_gross['Segment_End_HM'] = (show_theatre_gross['Segment_Start'] + show_theatre_gross['Total_Gross']) / 100000000
    
    # Create a color map for theatres (consistent colors across shows)
    unique_theatres = show_theatre_gross['Theatre'].unique()
    colors = px.colors.qualitative.Set3  # Using a qualitative color scheme
    color_map = {theatre: colors[i % len(colors)] for i, theatre in enumerate(unique_theatres)}
    
    # Create the figure
    fig = go.Figure()
    
    # Add segments for each show-theatre combination
    for _, segment in show_theatre_gross.iterrows():
        fig.add_trace(go.Bar(
            y=[segment['Show']],
            x=[segment['Total_Gross_HM']],
            base=[segment['Segment_Start_HM']],
            orientation='h',
            name=segment['Theatre'],
            marker=dict(color=color_map[segment['Theatre']]),
            hovertemplate=(
                f"<b>{segment['Show']}</b><br>"
                f"Theatre: {segment['Theatre']}<br>"
                f"Gross: ${segment['Total_Gross']:,.0f}<br>"
                f"Period: {segment['First_Week'].strftime('%Y-%m-%d')} to {segment['Last_Week'].strftime('%Y-%m-%d')}<br>"
                f"<extra></extra>"
            ),
            showlegend=False  # We'll handle legend separately
        ))
    
    # Create legend entries (one per theatre)
    for theatre, color in color_map.items():
        if theatre in show_theatre_gross['Theatre'].values:
            fig.add_trace(go.Scatter(
                x=[None], y=[None],
                mode='markers',
                marker=dict(size=10, color=color),
                legendgroup="theatres",
                name=theatre,
                showlegend=True
            ))
    
    # Update layout
    fig.update_layout(
        title='Top 40 Grossing Broadway Shows - Segmented by Theatre',
        xaxis_title='Total Gross ($ in Hundred-Millions)',
        yaxis_title='Show Name',
        barmode='stack',
        height=1200,  # Large height to show 40 shows
        showlegend=True,
        legend=dict(
            title='Theatres',
            orientation='v',
            yanchor='top',
            xanchor='left',
            x=1.05,
            y=1
        ),
        yaxis=dict(
            categoryorder='total ascending',  # Sort by total gross
            tickfont=dict(size=10)
        ),
        xaxis=dict(
            tickformat='$.1f'
        )
    )

    return fig


# 2) Average percentage capacity for each theatre to compare them by success
# 2.1) Also toggles to a plot of the number of unique shows at each for fun
def theatre_metric_plot(df, metric='capacity'):
    """
    Creates a dot plot showing either average capacity (or number of unique shows) by theatre
    """
    # Group by theatre and calculate both metrics
    theatre_data = df.groupby('Theatre').agg({
        '% Cap': 'mean',
        'Show': 'nunique'
    }).reset_index()
    
    # Determine which metric to use
    if metric == 'capacity':
        x_metric = '% Cap'
        x_title = 'Average Capacity (%)'
        x_format = {'ticksuffix': '%', 'range': [0, 100]}
        sort_metric = '% Cap'
        hover_template = '<b>%{y}</b><br>Avg Capacity: <b>%{x:.1f}%</b><br>Unique Shows: %{customdata}<extra></extra>'
    else:  # show_count
        x_metric = 'Show'
        x_title = 'Number of Unique Shows'
        x_format = {}  # No special formatting for count
        sort_metric = 'Show'
        hover_template = '<b>%{y}</b><br>Unique Shows: <b>%{x}</b><br>Avg Capacity: %{customdata:.1f}%<extra></extra>'
    
    # Sort by the selected metric
    theatre_data = theatre_data.sort_values(sort_metric, ascending=False)
    
    # Create scatter plot
    fig = px.scatter(
        theatre_data,
        x=x_metric,
        y='Theatre',
        title=f'Theatre Comparison: {x_title}',
        labels={
            x_metric: x_title,
            'Theatre': 'Theatre Name'
        }
    )
    
    # Apply consistent layout to the above chart
    fig.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white',
        height=max(800, len(theatre_data) * 18),
        margin=dict(l=200, r=50, t=80, b=50),
        
        title={
            'text': f'Theatre Comparison: {x_title}',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20}
        },
        
        yaxis={
            'categoryorder': 'total ascending',
            'tickfont': {'size': 10},
            'title': {'text': 'Theatre Name', 'font': {'size': 14}},
            'automargin': True
        },
        
        xaxis={
            'tickfont': {'size': 11},
            'title': {'text': x_title, 'font': {'size': 14}},
            **x_format  # Apply the format (suffix, range, etc.)
        }
    )
    
    # Set custom data for hover based on which metric isn't the primary one
    if metric == 'capacity':
        custom_data = theatre_data['Show']  # Show count in hover
    else:
        custom_data = theatre_data['% Cap']  # Capacity in hover
    
    # Enhanced marker styling
    fig.update_traces(
        marker=dict(
            size=8,
            color='#1f77b4',  # Consistent blue
            line=dict(width=1, color='darkblue')
        ),
        hovertemplate=hover_template,
        customdata=custom_data
    )
    
    return fig