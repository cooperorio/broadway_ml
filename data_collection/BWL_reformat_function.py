import pandas as pd

def BWL_reformat(bway_df):
    '''Informed by First Scrub Exploration, this function
    reformats the pandas dataframe containing Broadway League
    Data into a form that is more useable for analytics and
    Model building. input: pandas df; output: pandas df'''

    # First, I remove the potential leading column that was present
    # when read from the format of a saved pandas CSV:
    if 'Unnamed: 0' in bway_df.columns:
        bway_df = bway_df.drop('Unnamed: 0', axis=1)

    # Next, I rename the previous week columns in a format-robust manner, 
    # using 'LW' to denote 'last week'. Furthermore, sinceI will be 
    # removing the $ from the data, I rename the raw Grosses, too.
    bway_df = bway_df.rename(columns={'Grosses\nPrev Week': 'LW Grosses ($)',
                                      'Grosses Prev Week': 'LW Grosses ($)', 
                                      'Attend\nPrev Week': 'LW Attend',
                                      'Attend Prev Week': 'LW Attend',
                                      'Grosses': 'Grosses ($)'})
    
    # Then, I impute the empty financial & attendance values with 0s:
    bway_df['Grosses ($)'] = bway_df['Grosses ($)'].replace('$', '0', regex=False)
    bway_df['LW Grosses ($)'] = bway_df['LW Grosses ($)'].replace('$', '0', regex=False)
    bway_df['Attend'] = bway_df['Attend'].fillna('0')
    bway_df['LW Attend'] = bway_df['LW Attend'].fillna('0')

    # Finally, I make sure that all of my values are in analyzable formats, with
    # the numerical values as floats (for the sake of consistency), the titles, 
    # theatres, and show types as strings, and the Week Ends as dates.
    bway_df['Week End'] = pd.to_datetime(bway_df['Week End'])

    bway_df['Grosses ($)'] = bway_df['Grosses ($)'].str.replace('$', '').str.replace(',', '').astype(float)
    bway_df['LW Grosses ($)'] = bway_df['LW Grosses ($)'].str.replace('$', '').str.replace(',', '').astype(float)

    bway_df['Attend'] = bway_df['Attend'].str.replace(',', '').astype(float)
    bway_df['LW Attend'] = bway_df['LW Attend'].str.replace(',', '').astype(float)

    bway_df['% Cap'] = bway_df['% Cap'].str.replace('%', '').astype(float)

    bway_df['#Prev'] = bway_df['#Prev'].astype(float)
    bway_df['#Perf'] = bway_df['#Perf'].astype(float)

    return bway_df