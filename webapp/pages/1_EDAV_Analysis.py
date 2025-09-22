# pages/1_EDAV_Analysis.py
import streamlit as st
import pandas as pd
from analysis.test_functions import create_top_grossing_plot

st.set_page_config(page_title="EDAV Broadway Analysis", page_icon="📊")

st.title("📊 EDAV Broadway Analysis")

# Load data (you'll need to load it again or use st.session_state)
if 'df' in st.session_state:
    df = st.session_state.df
else:
    # Load data here or redirect to main page
    st.error("Please load data from the main page first")
    st.stop()

# 1) Show all-time top grossing chart
fig = create_top_grossing_plot(df)
st.plotly_chart(fig, use_container_width=True)

# 2...) Will add the rest of the functions to be used, here: