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
fig = top_grossing_segmented_bars(df)
st.plotly_chart(fig, use_container_width=True)

# Caption for context that theatre names change
st.caption(
    "Note: Theatre names are preserved as recorded historically, "
    "including name changes over time. For information on which theatres"
    "were renamed to which others, and which may no longer be active at all,"
    " see the following wikipedia page: "
    "https://en.wikipedia.org/wiki/List_of_Broadway_theaters#Active_Broadway_theaters"
    )

# 2...) Will add the rest of the functions to be used, here: