# pages/1_EDAV_Analysis.py
import streamlit as st
import pandas as pd
from analysis.test_functions import top_grossing_segmented_bars, theatre_capacity_plot

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

# 1.1) Caption for context that theatre names change
st.caption(
    "Note: Theatre names are preserved as recorded historically, "
    "including name changes over time. For information on which theatres"
    "were renamed to which others, and which may no longer be active at all,"
    " see the following wikipedia page: "
    "https://en.wikipedia.org/wiki/List_of_Broadway_theaters#Active_Broadway_theaters"
    )

# 2) Plot of the Theatres' grosses for comparison (not directly included
#    in the EDAV project, but inspired by its questions)
fig_theatre, princess_removed = theatre_capacity_plot(df)
st.plotly_chart(fig_theatre, use_container_width=True)

# Add context about the data & removal thereof
if princess_removed:
    st.caption(
        " Note: Princess Theatre has been removed from this visualization "
        "as its capacity values significantly exceed 100% (well over 200%), "
        "and considering its renaming (Latin Quarter) & subsequent discontinuation " 
        "as a Broadway Theatre, it will likely remain as such. For more information " 
        "on the Princess Theatre that was active in the 1980s, see the following " 
        "wikipedia article: "
        "https://en.wikipedia.org/wiki/Latin_Quarter_(nightclub)#Broadway_theatre"
    )

# 3...) W