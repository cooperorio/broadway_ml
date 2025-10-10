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

## 1) Show all-time top grossing chart
fig = top_grossing_segmented_bars(df)
st.plotly_chart(fig, use_container_width=True)

## 1.1) Caption for context that theatre names change
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
         being said, all 3 of the others have been running for a considerable period of time, with
         the newest (Hamilton) having been running since 2015. The 3 next highest grossing - The Book 
         of Mormon, Chicago, and Aladdin - are all not too far behind the billion mark; and seeing as 
         they are all still running with no signs of stopping any time soon, there is a good chance 
         that one (or more) of them may break that threshold in the somewhat near future.

Also interesting to investigate are the shows which transferred from one theatre to another during
         their production's run. Especially notable examples of this include The Lion King 
         transferring several years into its production from the New Amsterdam to the Minskoff, and 
         the wildly successful revival of Chicago transferring twice, beginning in the Richard
         Rodgers theatre, moving to the Shubert, and finding its longest home in the Ambassador. 
         The reasons for these transfers (sadly not included in the data set, but available through
         some basic sleuthing online - especially Playbill articles) are arguably more interesting 
         than the data itself. The most common reason for transfers I am aware of is when a new show 
         is already scheduled to occupy the theatre the transferring show is in. Check out some 
         example articles below on the Lion King's transver, and Chicago (1996)'s first transfer.

Links:
\nThe Lion King: https://playbill.com/article/circle-of-life-lion-king-reopens-at-the-minskoff-theatre-june-13-com-133141
\nChicago: https://playbill.com/article/chicago-transfers-to-the-shubert-today-com-329093


On the topic of the interplay between theatres and the shows they house, below we have the next 
         visualization of this page - a chart of the average capacity used for each theatre in 
         decreasing order:
""")


## 2) Plot of the Theatres' avg. capacities for comparison (not directly included
##    in the EDAV project, but inspired by its questions)
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
This plot, like the one before, was also altered from the one present in my original project, no
         longer showing the grosses for each theatre. I chose to switch over to the average occupied
         capacity of each of the theatres because I felt it would serve as a better point of comparison
         given that I wanted to preserve that some of the same theatres are represented under different 
         names, while also comparing across differently-sized theatres. For example, it shows that the
         Kit Kat Club ('24-'25; a renaming of the August Wilson Theatre) saw one of the highest average
         utilized capacities of the theatres I have data on (barring outliers - see caption). This 
         naming corresponds directly and solely with the 2024 Cabaret at the Kit Kat Club production,
         adding some insight into the success of that production.
         
You may notice that some theatres with some eerily similar names show up in this visualization. This
         is because the Broadway League reports its data with the current naming convention of the 
         theatre at the time, even if that name changes mid production. This led me to have to make
         the decision as to whether or not to aggregate the data based on physical location; and as
         you can see, I decided not to. This decision was motivated by a few factors (which I described 
         a little bit already above), with one major one being the added layer of unnecessary complexity I
         believe it would bring, given what I've already mentioned.


Now this next plot takes a more quantitatively rigorous approach to exploring the performance of 
         these shows - but in aggregate. Here, we see a plot of all of the grosses against their 
         respective attendance, attempting to fit a linear trend to this full data set:
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
leading to an increase of ticket prices (and by extension, grosses) in response to high demand, 
while selling the same number of tickets in total.

This all being said, this chart doesn't really give much insight into the data that one wouldn't
already usually be able to infer - that as attendance rises, grosses will tend to rise too. Perhaps
more interesting is to investigate if this is true for all types of shows, and (loosely) which type
sees this trend more strongly present, like in the next plot, which does as above, but faceted by
the show type.
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

st.write(f"""
Now we can get some more interesting insights. Firstly, not only do we see pretty clearly that
there are more performances that are musicals compared to plays, and far more performances that are
plays than there are specials. Beyond the obvious, we see that indeed the positive correlation
between attendance and grosses is indeed maintained for all show types, as should still be expected
due to the well established economic concept of supply-and-demand.

Secondly, we see that the 'pillaring' I mentioned before in the data is primarily seen with the data
from the musicals, suggesting that the phenomenon of ticket prices rising after selling out the 
venue regularly is a more frequent occurrence with musicals when compared to the other show types - 
in raw numbers at least. It still happens with some plays, but it seems far less frequent there.

Thirdly, the above point is likely a driving factor in the fact that the percent of the variation in 
gross revenue that can be explained by attendance (R²) is greatest among the plays' data when compared
to the other show types' data.

With that all being said, this doesn't give us much insight on what is going on in the data over
time. As such, I decided to take a look at the total grosses and attendance over time to see how
they relate (showing their pearson correlation coefficient directly) in the next graph:
""")

# 5) Joint gross & attendance data vs time
fig_combined = combined_gross_attendance_timeseries(df)
st.plotly_chart(fig_combined, use_container_width=True)

st.caption(
    "Note: the grosses are not adjusted for inflation."
)

st.write(f"""
While not offering too much more than one might already be able to infer - that grosses and attendance
         do seem to correlate over time, seeing it graphically still does illuminate some interesting
         aspects of the relationship. For one thing, you can see that the fact that the grosses not
         being adjusted for inflation clearly has an impact on the data, with such adjustments likely
         allowing the two trendlines to match up even more closely than they do here.

Also interesting to see are the impacts that major events since 1980 had on the data, both in grosses
         and in attendance. For example, you can see 4 clear synchronated drops in both attendance
         and grosses, and when zooming in, you can link these to different events happening in either
         NYC, globally, or even just the broadway industry specifically. For example the first downward
         spike corresponds with the September 11th attacks on the World Trade Center in 2001 - an
         event which had a large impact on tourism to NYC shortly after. Next, in March 2003 & 
         November 2007, we see what is likely the affect of the major Broadway Musicians and 
         the Broadway Stagehands Strikes respectively, groups both of which are necessary for the 
         great white way to function. Finally, we see the prolonged dip (or more accurately on the
         back-end, lack of data) between early 2020 and later 2021 which is the direct result of the
         COVID 19 pandemic on the Broadway community, being forced to shut down entirely during this time.

Though this is all quite interesting to see, it is still quite broad in scope. As such, I decided to 
         hone in a bit in the final two visualizations, looking at the data over time in a more focused
         manner, and taking a look at potential seasonality patterns month by month (respectively):
""")

st.header("Brief & Early Look at Time Series & Seasonality")

# 6) Time series for several metrics, faceted by show type:
show_type_timeseries_analysis(df)

st.write(f"""
Here, we can see all sorts of peculiarities in the data, plotting the grosses, the (calculated) average
         ticket prices, and average percent capacity, and faceting by show type. Firstly, in the plot
         of the grosses, we can see quite clearly that the total grosses from musicals seem to 
         consistently outpace the grosses from both plays and specials combined! Though this is likely
         no surprise to anyone who has experienced NYC, as advertisements for musicals are just about
         everywhere. Not only that, but typically there are far more musicals than plays or specials
         playing in broadway theatres at any given time. Due to this volume imbalance, it made sense
         to look at the average ticket prices of each for a more consistent comparison.

In this second chart with the average ticket prices, we can see that they are actually quite similar
         from show type to show type. One notable exception is what seems to be a ticket price
         explosion for specials between October 2017 and December 2018. This can be attributed to 
         Springsteen On Broadway, which had an average ticket price of around $500 during its run.

The third chart with the percent capacities seems to show that musicals tend to fill slightly more of
         their theatre's capacity on average compared to plays. Specials, however, seem to show a much
         more inconsistent trend, likely due to more sparse data. Ignoring this sparsity, though, we 
         see one absolutely massive outlier in 1983 that manages to affect the scale of the whole chart!
         Upon digging deeper, I found this to be due to the data from The Flying Karamazov Brothers in
         reporting week 05/15/1983 reporting a percent capacity occupancy of 903%. This is still present
         on the Broadway League's website itself, but looking at all of the other parameters, it seems
         to have been a typical week coming out of previews. This leads me to believe this is a reporting
         or clerical error on Broadway League's part.


Finally, we have the chart plotting the seasonality of several facets of the data in aggregate, both for
         interest, and for a last bit of confirmation that time series analysis in later parts of this
         project should be a special focus, rather than just traditional Machine Learning (which will
         still be explored regardless):
""")

# 7) Seasonality for several metrics.
display_seasonality_analysis(df)

### Note to self - the legends for the first of these visualisations (the part on attendance) 
### are not consistent, and need to be altered.

st.write(f"""

""")