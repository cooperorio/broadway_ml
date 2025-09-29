# pages/1_EDAV_Analysis.py
import streamlit as st
import pandas as pd
from analysis.test_functions import top_grossing_segmented_bars, theatre_capacity_plot
from analysis.test_functions import gross_vs_attendance_regression_plot, display_regression_summary
from analysis.test_functions import gross_vs_attendance_by_show_type, display_faceted_analysis_results
from analysis.test_functions import combined_gross_attendance_timeseries, show_type_timeseries_analysis

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

# 3) Grosses vs. Attendance Linear Plot & Regression
fig_gross_attend, regression_model = gross_vs_attendance_regression_plot(df)
st.plotly_chart(fig_gross_attend, use_container_width=True)

# 3.1) Display the regression summary
display_regression_summary(regression_model)

# Interpretation
st.subheader("Interpretation")
intercept = regression_model.params['const']
slope = regression_model.params['Attend']
r_squared = regression_model.rsquared

st.write(f"""
The linear regression model suggests that for each additional attendee, 
weekly gross revenue increases by **${slope:.2f}** on average.

- **Intercept (${intercept:,.0f})**: This *would* be the estimated base revenue when attendance is
                                     zero, but because grosses here are reported as always positive, 
                                     being the total amount of money brought in through ticket
                                     sales, it isn't really interpretable in a meaningful way.
- **Slope (${slope:.2f})**: The estimated revenue per additional attendee.
- **R² ({r_squared:.3f})**: {r_squared*100:.1f}% of the variation in gross revenue 
                            can be explained by attendance.

Here you can see that the data sees a much greater spread as the attendance/ticket sales increase,
and coupling this with the only moderately-sized R² value present, and the not insignificant
portion of the line of best fit dipping into the negative, it is likely that the relationship here,
though significant, is not strictly linear.

The above is further evidenced by the phenomenon of vertical pillars of data visible in the plot.
This can probably be explained by theatres housing particularly popular shows selling out entirely,
leading to an increase of ticket prices (and by extension, grosses), while selling the same number
of tickets in total.

******add information about how this motivates the next plot HERE
""")

# 4) Faceted the gross vs attendance by show type
fig_faceted, regression_stats = gross_vs_attendance_by_show_type(df)
st.plotly_chart(fig_faceted, use_container_width=True)

# Add context and interpretation
st.caption(
    "This chart shows how the relationship between attendance and revenue varies across "
    "different types of shows. Each subplot represents a different show category. "
    "The red trendlines help visualize the general pattern for each show type."
)

# Statistical parameters
display_faceted_analysis_results(regression_stats)

# Optional: Add some quick statistics
with st.expander("Show Type Statistics"):
    type_stats = df.groupby('Type').agg({
        'Grosses ($)': ['mean', 'count'],
        'Attend': 'mean',
        '% Cap': 'mean'
    }).round(2)
    
    # Flatten column names
    type_stats.columns = ['_'.join(col).strip() for col in type_stats.columns.values]
    type_stats = type_stats.rename(columns={
        'Grosses ($)_mean': 'Avg Weekly Gross',
        'Grosses ($)_count': 'Weeks Recorded',
        'Attend_mean': 'Avg Attendance',
        '% Cap_mean': 'Avg Capacity'
    })
    
    st.dataframe(type_stats.style.format({
        'Avg Weekly Gross': '${:,.0f}',
        'Avg Attendance': '{:,.0f}',
        'Avg Capacity': '{:.1f}%'
    }))

#5) Joint gross & attendance data vs time
fig_combined = combined_gross_attendance_timeseries(df)
st.plotly_chart(fig_combined, use_container_width=True)

st.caption(
    "Note: the grosses are not adjusted for inflation."
)

# 6) Time series for several metrics, faceted by show type:
show_type_timeseries_analysis(df)