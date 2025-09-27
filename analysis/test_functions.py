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
import statsmodels.api as sm
from scipy import stats


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
def theatre_capacity_plot(df):
    """
    Create a dot plot showing average percent capacity by theatre with show count in hover
    """
    # Group by theatre and calculate metrics
    theatre_data = df.groupby('Theatre').agg({
        '% Cap': 'mean',
        'Show': 'nunique'
    }).reset_index()
    
    # Remove Princess theatre if it's a significant outlier. Considering
    # its renaming & discontinuation, it likely will be an outlier from now on.
    princess_capacity = theatre_data[theatre_data['Theatre'] == 'Princess']
    if not princess_capacity.empty and princess_capacity['% Cap'].iloc[0] > 100:
        theatre_data = theatre_data[theatre_data['Theatre'] != 'Princess']
        princess_removed = True
    else:
        princess_removed = False
    
    # Sort by average capacity in descending order
    theatre_data = theatre_data.sort_values('% Cap', ascending=False)
    
    # Create scatter plot
    fig = px.scatter(
        theatre_data,
        x='% Cap',
        y='Theatre',
        title='Average Capacity Utilization by Theatre',
        labels={
            '% Cap': 'Average Capacity (%)',
            'Theatre': 'Theatre Name'
        }
    )
    
    # Calculate dynamic x-axis range (cap at 100% unless there are values above)
    x_max = max(theatre_data['% Cap'].max(), 100)
    x_range = [0, x_max * 1.05]  # 5% padding
    
    # Apply consistent layout
    fig.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white',
        height=max(800, len(theatre_data) * 18),
        margin=dict(l=200, r=50, t=80, b=50),
        
        title={
            'text': 'Average Capacity Utilization by Theatre',
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
            'ticksuffix': '%',
            'range': x_range,  # Dynamic range
            'tickfont': {'size': 11},
            'title': {'text': 'Average Capacity (%)', 'font': {'size': 14}}
        }
    )
    
    # Enhanced marker styling
    fig.update_traces(
        marker=dict(
            size=8,
            color='#1f77b4',  # Consistent blue
            line=dict(width=1, color='darkblue')
        ),
        hovertemplate=(
            '<b>%{y}</b><br>'
            'Average Capacity: <b>%{x:.1f}%</b><br>'
            'Number of Shows: %{customdata}<extra></extra>'
        ),
        customdata=theatre_data['Show']  # Show count in hover
    )
    
    return fig, princess_removed

# 3) Grosses vs. Attendance w/ Linear Fit
def gross_vs_attendance_regression_plot(df):
    """
    Create a scatter plot with linear regression using statsmodels
    """
    # First, I remove rows with missing values
    plot_data = df[['Attend', 'Grosses ($)']].dropna()
    
    # Then I prepare data for the statsmodels regression...
    X = plot_data['Attend']  # Independent variable
    y = plot_data['Grosses ($)']  # Dependent variable
    
    # ...add constant for intercept to make it work with statsmodels...
    X = sm.add_constant(X)
    
    # ... and perform ordinary linear regression
    model = sm.OLS(y, X).fit()
    
    # Then I create the scatter plot...
    fig = px.scatter(
        plot_data,
        x='Attend',
        y='Grosses ($)',
        title='Weekly Gross vs Weekly Attendance with Linear Regression',
        labels={
            'Attend': 'Attendance',
            'Grosses ($)': 'Gross ($)'
        },
        opacity=0.3
    )
    
    # ... and add regression line using the model parameters
    x_range = np.linspace(plot_data['Attend'].min(), plot_data['Attend'].max(), 100)
    X_pred = sm.add_constant(x_range)
    y_pred = model.predict(X_pred)
    
    fig.add_trace(go.Scatter(
        x=x_range,
        y=y_pred,
        mode='lines',
        line=dict(color='red', width=3),
        name='Linear Regression Fit'
    ))
    
    # Then I apply a consistent layout with my other charts
    fig.update_layout(
        plot_bgcolor='white',        # Matches your other charts
        paper_bgcolor='white',       # Matches your other charts
        height=600,                  # Consistent height with other plots
        margin=dict(l=50, r=50, t=80, b=50),  # Prevents label cropping
        
        title={
            'text': 'Weekly Gross vs Weekly Attendance with Linear Regression',
            'x': 0.5,                # Centers the title (important!)
            'xanchor': 'center',      # Centers the title
            'font': {'size': 20}      # Matches your other chart titles
        },
        
        yaxis={
            'tickfont': {'size': 11},
            'title': {'text': 'Gross ($)', 'font': {'size': 14}},
            'tickformat': '$,.0f'    # Formats as currency - CRITICAL!
        },
        
        xaxis={
            'tickfont': {'size': 11},
            'title': {'text': 'Attendance', 'font': {'size': 14}}
        }
    )
    
    return fig, model

# 3.1)... and a function to display the analysis more clearly
def display_regression_summary(model):
    """
    Display regression summary in a format similar to R's summary(lm())
    """
    st.subheader("Linear Regression Summary")
    
    # Create a summary similar to R's output
    summary_data = []
    
    # Coefficients table (like R's Coefficients section)
    st.write("**Coefficients:**")
    coef_df = pd.DataFrame({
        'Estimate': model.params,
        'Std. Error': model.bse,
        't value': model.tvalues,
        'Pr(>|t|)': model.pvalues
    })
    
    # Format p-values with stars like R does
    def format_pvalue(p):
        if p < 0.001:
            return f"{p:.4f} ***"
        elif p < 0.01:
            return f"{p:.4f} **"
        elif p < 0.05:
            return f"{p:.4f} *"
        elif p < 0.1:
            return f"{p:.4f} ."
        else:
            return f"{p:.4f}"
    
    coef_df['Pr(>|t|)'] = coef_df['Pr(>|t|)'].apply(format_pvalue)
    st.dataframe(coef_df.style.format({
        'Estimate': '{:.2f}',
        'Std. Error': '{:.2f}',
        't value': '{:.2f}'
    }))
    
    st.caption("Significance codes: *** p < 0.001, ** p < 0.01, * p < 0.05, . p < 0.1")
    
    # Model statistics (like R's bottom section)
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("R-squared", f"{model.rsquared:.4f}")
    
    with col2:
        st.metric("Adj. R-squared", f"{model.rsquared_adj:.4f}")
    
    with col3:
        st.metric("F-statistic", f"{model.fvalue:.2f}")
    
    with col4:
        st.metric("P-value (F)", f"{model.f_pvalue:.4f}")
    
    # Additional statistics
    st.write("**Model Statistics:**")
    stats_df = pd.DataFrame({
        'Statistic': ['Observations', 'Df Residuals', 'Df Model'],
        'Value': [model.nobs, model.df_resid, model.df_model]
    })
    st.dataframe(stats_df, hide_index=True)
    
    # Diagnostic information
    st.write("**Residual Statistics:**")
    residuals = model.resid
    resid_df = pd.DataFrame({
        'Statistic': ['Min', '1Q', 'Median', '3Q', 'Max'],
        'Value': [
            residuals.min(),
            np.percentile(residuals, 25),
            np.median(residuals),
            np.percentile(residuals, 75),
            residuals.max()
        ]
    })
    st.dataframe(resid_df.style.format({'Value': '{:.2f}'}), hide_index=True)