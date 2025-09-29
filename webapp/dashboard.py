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
from utils.shared import get_data

# That's almost all that we need now that we offloaded most
# of the other functions to our utils file (data loading, at least)
st.set_page_config(
    page_title="Broadway Data Dashboard",
    page_icon="🎭",
    layout="wide"
)

# Just a function to make our filtered dataframe based 
# on sidebar inputs for this dashboard page in particular.
def apply_filters(df):
    """Apply sidebar filters to the data"""
    df_filtered = df.copy()
    
    st.sidebar.header("Filters")
    
    # Date range filter
    if 'Week End' in df_filtered.columns:
        min_date = df_filtered['Week End'].min()
        max_date = df_filtered['Week End'].max()
        
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
            # Default to my guess at the most popular shows
            default=['HAMILTON', 'WICKED', 'THE PHANTOM OF THE OPERA', 
                     'THE LION KING', 'HADESTOWN']  
        )
        df_filtered = df_filtered[df_filtered['Show'].isin(shows)]
    
    return df_filtered


def main():
    st.title("🎭 Broadway Data Dashboard")
    st.markdown("Welcome to the Broadway data analysis dashboard! Take a look around and explore historical Broadway performance data with interactive visualizations.")
    
    # Load data
    df = get_data()
    if df is None:
        st.error("Failed to load data. Please check your credentials and try again.")
        return
    
    # Apply filters
    df_filtered = apply_filters(df)
    
    # Key metrics at the top
    st.subheader("Key Performance Indicators")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if len(df_filtered) > 0 and 'Show' in df_filtered.columns:
            total_shows = len(df_filtered['Show'].unique())
            st.metric("Total Shows", total_shows)
        else:
            st.metric("Total Shows", 0)

    with col2:
        if len(df_filtered) > 0 and 'Grosses ($)' in df_filtered.columns:
            total_gross = df_filtered['Grosses ($)'].sum()
            st.metric("Total Gross", f"${total_gross:,.0f}")
        else:
            st.metric("Total Gross", "$0")

    with col3:
        if len(df_filtered) > 0 and 'Attend' in df_filtered.columns:
            avg_attendance = df_filtered['Attend'].mean()
            st.metric("Average Attendance", f"{avg_attendance:,.0f}")
        else:
            st.metric("Average Attendance", 0)

    with col4:
        if len(df_filtered) > 0 and '% Cap' in df_filtered.columns:
            avg_capacity = df_filtered['% Cap'].mean()
            st.metric("Average Capacity (%)", f"{avg_capacity:.1f}%")
        else:
            st.metric("Average Capacity (%)", "0.0%")
    

    st.subheader("Individual Show Performance Over Time")

    if len(df_filtered) > 0:
        # Build available metrics based on what's in the dataframe
        metric_options = []
        metric_mapping = {}
        
        if 'Grosses ($)' in df_filtered.columns:
            metric_options.append('Grosses')
            metric_mapping['Grosses'] = 'Grosses ($)'
        
        if 'Attend' in df_filtered.columns:
            metric_options.append('Attendance') 
            metric_mapping['Attendance'] = 'Attend'
        
        if '% Cap' in df_filtered.columns:
            metric_options.append('Capacity %')
            metric_mapping['Capacity %'] = '% Cap'
        
        if metric_options:
            selected_metric_display = st.radio(
                "View by:",
                options=metric_options,
                horizontal=True,
                key="metric_selector"
            )
            
            # Get the actual column name from the mapping
            selected_metric = metric_mapping[selected_metric_display]
            
            # Create the chart with the selected metric
            if 'Week End' in df_filtered.columns and 'Show' in df_filtered.columns:
                # Set appropriate title and labels
                title_map = {
                    'Grosses ($)': 'Weekly Grosses by Show Over Time',
                    'Attend': 'Weekly Attendance by Show Over Time', 
                    '% Cap': 'Weekly Capacity by Show Over Time'
                }
                
                y_label_map = {
                    'Grosses ($)': 'Weekly Gross ($)',
                    'Attend': 'Weekly Attendance',
                    '% Cap': 'Capacity (%)'
                }
                
                fig = px.line(df_filtered, x='Week End', y=selected_metric, 
                            color='Show',
                            title=title_map.get(selected_metric, f'Weekly {selected_metric} by Show'),
                            labels={selected_metric: y_label_map.get(selected_metric, selected_metric), 
                                    'Week End': 'Date'})
                
                fig.update_layout(height=500)
                st.plotly_chart(fig, use_container_width=True)
                
                st.caption(
                    "Note: the grosses are not adjusted for inflation."
                )

                # Performance summary (adapts to available columns)
                st.subheader("Show Performance Summary")
                
                # Determine which columns to include
                agg_dict = {}
                if 'Grosses ($)' in df_filtered.columns:
                    agg_dict['Grosses ($)'] = ['sum', 'mean', 'max']
                if 'Attend' in df_filtered.columns:
                    agg_dict['Attend'] = ['mean']
                if '% Cap' in df_filtered.columns:
                    agg_dict['% Cap'] = ['mean']
                
                if agg_dict:  # Only proceed if we have columns to aggregate
                    show_stats = df_filtered.groupby('Show').agg(agg_dict).round(2)
                    
                    # Flatten column names
                    show_stats.columns = ['_'.join(col).strip() for col in show_stats.columns.values]
                    
                    # Rename for readability
                    column_renames = {
                        'Grosses ($)_sum': 'Total_Gross',
                        'Grosses ($)_mean': 'Avg_Weekly_Gross',
                        'Grosses ($)_max': 'Peak_Weekly_Gross', 
                        'Attend_mean': 'Avg_Attendance',
                        '% Cap_mean': 'Avg_Capacity'
                    }
                    show_stats = show_stats.rename(columns=column_renames)
                    
                    # Sort by total gross if available, otherwise by first column
                    sort_column = 'Total_Gross' if 'Total_Gross' in show_stats.columns else show_stats.columns[0]
                    show_stats = show_stats.sort_values(sort_column, ascending=False)
                    
                    # Format display
                    format_dict = {}
                    if 'Total_Gross' in show_stats.columns:
                        format_dict['Total_Gross'] = '${:,.0f}'
                    if 'Avg_Weekly_Gross' in show_stats.columns:
                        format_dict['Avg_Weekly_Gross'] = '${:,.0f}'
                    if 'Peak_Weekly_Gross' in show_stats.columns:
                        format_dict['Peak_Weekly_Gross'] = '${:,.0f}'
                    if 'Avg_Attendance' in show_stats.columns:
                        format_dict['Avg_Attendance'] = '{:,.0f}'
                    if 'Avg_Capacity' in show_stats.columns:
                        format_dict['Avg_Capacity'] = '{:.1f}%'
                    
                    st.dataframe(show_stats.style.format(format_dict))
        else:
            st.info("No numeric metrics available for visualization")
    else:
        st.info("No data available for visualization with current filters")
    

    # Recent Data Preview
    st.subheader("Recent Data Preview")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        if len(df_filtered) > 0:
            st.dataframe(df_filtered.tail(10), use_container_width=True)
        else:
            st.info("No data available with current filters")

    with col2:
        st.write("**Data Summary:**")
        st.write(f"**Total Records:** {len(df_filtered):,}")
        
        # Safe date range display
        if len(df_filtered) > 0 and 'Week End' in df_filtered.columns:
            min_date = df_filtered['Week End'].min()
            max_date = df_filtered['Week End'].max()
            if not pd.isna(min_date) and not pd.isna(max_date):
                st.write(f"**Date Range:** {min_date.strftime('%Y-%m-%d')} to {max_date.strftime('%Y-%m-%d')}")
            else:
                st.write("**Date Range:** Invalid dates")
        else:
            st.write("**Date Range:** No data available")
        
        # Safe theatre count
        if len(df_filtered) > 0 and 'Theatre' in df_filtered.columns:
            st.write(f"**Theatres:** {df_filtered['Theatre'].nunique()}")
        else:
            st.write("**Theatres:** 0")
    
    # Call to action for other pages
    st.markdown("---")
    st.subheader("Explore More Analysis")
    st.markdown("""
    Interested in diving deeper? Check out my more pointed analyses & visualizations:
    
    - **📊 EDAV Analysis**: See visualizations inspired by my previous coursework!
    - **🤖 Machine Learning**: Predictive models and advanced analytics
    - **More pages coming soon...**
    """)

if __name__ == "__main__":
    main()