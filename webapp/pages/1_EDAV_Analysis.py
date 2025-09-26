# pages/1_EDAV_Analysis.py
import streamlit as st
import pandas as pd
from analysis.test_functions import top_grossing_segmented_bars

st.set_page_config(
    page_title="EDAV Broadway Analysis",
    page_icon="📊",
    layout="wide"
)

st.title("📊 EDAV Broadway Analysis")

# Load data (you'll need to load it again or use st.session_state)
if 'df' in st.session_state:
    df = st.session_state.df
else:
    # Load data here or redirect to main page
    st.error("Please load data from the main page first")
    st.stop()

# 1) Show all-time top grossing chart
try:
    # Use the complex version for full functionality
    fig = top_grossing_segmented_bars(df)
    st.plotly_chart(fig, use_container_width=True)
    
    # Add your caption here (Option 1)
    st.caption(
        "Note: Theatre names are preserved as recorded historically, "
        "including name changes over time. For information on which theatres"
        "were renamed to which others, and which may no longer be active at all,"
        " see the following wikipedia page: "
        "https://en.wikipedia.org/wiki/List_of_Broadway_theaters#Active_Broadway_theaters"
        )
        
except Exception as e:
    st.error(f"Error creating segmented bar chart: {e}")
    # Fallback to simple dot plot
    st.info("Falling back to dot plot version...")
    try:
        fig_fallback = top_grossing_plot(df)
        st.plotly_chart(fig_fallback, use_container_width=True)
    except Exception as e2:
        st.error(f"Error with fallback chart: {e2}")

fig = top_grossing_segmented_bars(df)
st.plotly_chart(fig, use_container_width=True)

# 2...) Will add the rest of the functions to be used, here: