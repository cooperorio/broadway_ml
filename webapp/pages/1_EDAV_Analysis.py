# pages/1_EDAV_Analysis.py
import streamlit as st
import pandas as pd
from analysis.test_functions import top_grossing_segmented_bars, theatre_capacity_plot
from analysis.test_functions import gross_vs_attendance_regression_plot, display_regression_summary
from analysis.test_functions import gross_vs_attendance_by_show_type, display_faceted_analysis_results
from analysis.test_functions import combined_gross_attendance_timeseries, show_type_timeseries_analysis
from analysis.test_functions import monthly_seasonality_analysis, display_seasonality_analysis

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

st.write(f"""
Welcome to the 'EDAV' page of my Broadway Data analytics project!
         
'EDAV' in this case stands for 'Exploratory Data Analysis & Visualization', and as you might expect
with such a title, this is the section where I do some more nuanced visualizations of the data itself
compared to just what we can see from the dashboard. Additionally, you will find here some cursory
statistical analysis when relevant for exploring the data more generally.
         
That being said, this is not the only reason why this page is named as it is. The visualizations and
explanations found on this page primarily consist of work that is analogous to the work I and my project
partner, Aylmer Liang, completed for our EDAV course's final project. That project (which planted the
seeds of inspiration for this one) was primarily written in R, so this took some translation to get 
where it is now. Additionally, many of the charts were either combined, left out, or strongly altered 
for the sake of reducing redundancy and making for a more streamlined viewing experience.
         
If you are curious to see the original work done for this course (done on a more limited dataset),
visit the following link: https://aylmergit.github.io/Broadway/
         
Now on to the visualizations!!
""")

# 1) Show all-time top grossing chart
fig = top_grossing_segmented_bars(df)
st.plotly_chart(fig, use_container_width=True)

# 1.1) Caption for context that theatre names change
st.caption(
    "Note: theatre names are preserved as recorded historically, "
    "including name changes over time. For information on which theatres "
    "were renamed to which others, and which may no longer be active at all,"
    " see the following wikipedia page: "
    "https://en.wikipedia.org/wiki/List_of_Broadway_theaters#Active_Broadway_theaters"
    )

st.write(f"""
Above you can see the top 40 grossing show runs since the early 1980s. You may notice some names that 
         are very similar where it seems as though the are present more than once. This is due to 
         their names changing in the Broadway League's reporting - typically due to either an 
         extended hiatus, or changes to the script (ex. Harry Potter) that were substantial enough 
         to warrant that change, despite technically being considered the same production.

Exploring the data itself further, you can see that only 4 shows have broken the billion dollar 
         mark in show run grosses (at time of writing). Of these 4 shows (The Lion King, 
         Wicked, The Phantom of the Opera, and Hamilton), only one has concluded its record setting
         run, that being the longest ever running show on Broadway, The Phantom of the Opera. That
         being said, the 3 next highest grossing - The Book of Mormon, Chicago, and Aladdin - are 
         all not too far behind the billion mark; and seeing as they are all still running with no 
         signs of stopping any time soon, there is a good chance that one (or more) of them may 
         break that threshold in the somewhat near future.

Also interesting to investigate are the shows which transferred from one theatre to another during
         their production's run. Especially notable examples of this include The Lion King 
         transferring several years into its production from the New Amsterdam to the Minskoff, and 
         the wildly successful revival of Chicago transferring twice, beginning in the Richard
         Rodgers theatre, moving to the Shubert, and finding its longest home in the Ambassador. 
         The reasons for these transfers (sadly not included in the data set, but available through
         some basic sleuthing online - especially Playbill articles) are arguably more interesting 
         than the data itself.
         
         The most common reason for transfers I am aware of is when a new show is already scheduled to
         occupy the theatre the transferring show is in. When the current show at the time is still
         performing very well, against initial plans or expectations, it may then move its production
         to an entirely new theatre and continue on (like in the case of Chicago's first transfer). 
         This can also be a more planned process, however, like with the Lion King's transfer to 
         make way for Marry Poppins, where both were produced by the same company. [see links below,  
         or view their respective wikis for more a little more information on these specific cases]

Links:
         The Lion King: https://playbill.com/article/circle-of-life-lion-king-reopens-at-the-minskoff-theatre-june-13-com-133141
         Chicago: https://playbill.com/article/chicago-transfers-to-the-shubert-today-com-329093


On the topic of the interplay between theatres and the shows they house, below we have the next 
         visualization of this page - a chart of the average capacity used for each theatre in 
         decreasing order:
""")


# 2) Plot of the Theatres' avg. capacities for comparison (not directly included
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

st.write(f"""
You may notice that some theatres with some eerily similar names show up in this visualization. This
         is because the Broadway League reports its data with the current naming convention of the 
         theatre at the time, even if that name changes mid production. This led me to have to make
         the decision as to whether or not to aggregate the data based on physical location; and as
         you can see, I decided not to. This decision was motivated by a few factors (which I describe a
         little bit further below), with one major one being the added layer of unnecessary complexity I
         believe it would bring
         
This plot, like the one before, was also altered from the one present in my original project, no
         longer showing the grosses for each theatre. I chose to switch over to the average occupied
         capacity of each of the theatres because I felt it would serve as a better point of comparison
         given that I wanted to preserve that some of the same theatres are represented under different 
         names, while also comparing across differently-sized theatres. For example, it shows that the
         Kit Kat Club ('24-'25; a renaming of the August Wilson Theatre) saw one of the highest average
         utilized capacities of the theatres I have data on (barring outliers - see caption). This 
         naming corresponds directly and solely with the 2024 Cabaret at the Kit Kat Club production,
         adding some insight into the success of that production.
""")

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

st.header("Brief & early look at Time Series & Seasonality")

# 6) Time series for several metrics, faceted by show type:
show_type_timeseries_analysis(df)

# 7) Seasonality for several metrics.
display_seasonality_analysis(df)