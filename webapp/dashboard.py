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
        total_shows = len(df_filtered['Show'].unique())
        st.metric("Total Shows", total_shows)
    
    with col2:
        if 'Grosses ($)' in df_filtered.columns:
            total_gross = df_filtered['Grosses ($)'].sum()
            st.metric("Total Gross", f"${total_gross:,.0f}")
    
    with col3:
        if 'Attend' in df_filtered.columns:
            avg_attendance = df_filtered['Attend'].mean()
            st.metric("Average Attendance", f"{avg_attendance:,.0f}")
    
    with col4:
        if 'Capacity' in df_filtered.columns:
            avg_capacity = df_filtered['Capacity'].mean()
            st.metric("Average Capacity", f"{avg_capacity:.1f}%")
    

    st.subheader("Individual Show Grosses Over Time")

    if 'Grosses ($)' in df_filtered.columns and 'Week End' in df_filtered.columns and 'Show' in df_filtered.columns:
        # Create the line chart with each show as a separate line
        fig = px.line(df_filtered, x='Week End', y='Grosses ($)', 
                    color='Show',
                    title='Weekly Grosses by Show Over Time',
                    labels={'Grosses ($)': 'Weekly Gross ($)', 'Week End': 'Date'})
        
        # Simple layout customization
        fig.update_layout(height=500)
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Simple performance summary
        st.subheader("📊 Show Performance Summary")
        
        show_stats = df_filtered.groupby('Show').agg({
            'Grosses ($)': ['sum', 'mean', 'max'],
            'Attend': 'mean'
        }).round(2)
        
        # Flatten the column names
        show_stats.columns = ['Total_Gross', 'Avg_Weekly_Gross', 'Peak_Weekly_Gross', 'Avg_Attendance']
        show_stats = show_stats.sort_values('Total_Gross', ascending=False)
        
        # Display the summary table
        st.dataframe(show_stats.style.format({
            'Total_Gross': '${:,.0f}',
            'Avg_Weekly_Gross': '${:,.0f}',
            'Peak_Weekly_Gross': '${:,.0f}',
            'Avg_Attendance': '{:,.0f}'
        }))
    
    ###### Maybe I will try to incorporate this here later, ######
    ###### but for now it just feels a little cluttered...  ######
    # # Top Shows This Period
    # st.subheader("Top Performing Shows (Selected Period)")
    
    # if 'Show' in df_filtered.columns and 'Grosses ($)' in df_filtered.columns:
    #     top_shows = df_filtered.groupby('Show').agg({
    #         'Grosses ($)': 'sum',
    #         'Attend': 'sum',
    #         'Theatre': 'first'
    #     }).nlargest(10, 'Grosses ($)').reset_index()
        
    #     col1, col2 = st.columns([2, 1])
        
    #     with col1:
    #         # Bar chart of top shows
    #         fig_bar = px.bar(top_shows, x='Grosses ($)', y='Show', 
    #                        title='Top 10 Shows by Gross Revenue',
    #                        color='Grosses ($)',
    #                        color_continuous_scale='viridis')
    #         fig_bar.update_layout(height=400)
    #         st.plotly_chart(fig_bar, use_container_width=True)
        
    #     with col2:
    #         # Display as a table
    #         st.write("**Top Shows Summary:**")
    #         for i, (_, show) in enumerate(top_shows.iterrows()):
    #             st.write(f"{i+1}. **{show['Show']}**")
    #             st.write(f"   ${show['Grosses ($)']:,.0f}")
    #             if i < 4:  # Only show first 5 to save space
    #                 st.write("")
    
    # Recent Data Preview
    st.subheader("🔍 Recent Data Preview")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        #41 because there are 41 Broadway showhouses
        st.dataframe(df_filtered.tail(41), use_container_width=True)
    
    with col2:
        st.write("**Data Summary:**")
        st.write(f"**Total Records:** {len(df_filtered):,}")
        st.write(f"**Date Range:** {df_filtered['Week End'].min().strftime('%Y-%m-%d')} to {df_filtered['Week End'].max().strftime('%Y-%m-%d')}")
        st.write(f"**Theatres:** {df_filtered['Theatre'].nunique()}")
    
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