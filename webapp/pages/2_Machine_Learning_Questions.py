# webapp/pages/2_Machine_Learning_Questions.py
import streamlit as st
import pandas as pd
from sklearn.linear_model import LinearRegression
from utils.shared import get_data

st.set_page_config(
    page_title="ML Questions & Analysis",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 Machine Learning Questions & Analysis")

# Load data
df = get_data()
if df is None:
    st.error("No data available. Please check the main page.")
    st.stop()

st.header("Predictive Modeling")

# Placeholder for ML content
st.info("""
This section is under development. Planned analyses include:

- Revenue prediction models
- Attendance forecasting
- Show success classification
- Seasonal trend analysis
""")