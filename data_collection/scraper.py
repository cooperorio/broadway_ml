# Written by Cooper Orio for Broadway Data Project

# My Selenium imports, most of which will be used I think(?)
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from datetime import date, timedelta
import time
import os
import sys
from BWL_reformat_function import BWL_reformat

# Before doing any real work with the driver I will use to scrub the website, I first
# make a list of start_date-end_date pairs to be entered into the search bar when
# we are able to query the page. If the csv already exists, rather than starting
# from the beginning, it checks for the most recent date, and sets that as the start
# date fror the remainder of the scraping.

# first a function to generate Sundays to iterate over:
def all_sundays_between(start_date, end_date):
    sundays = []
    current_date = start_date
    while current_date <= end_date:
        if current_date.weekday() == 6:  # Sunday is represented by 6
            sundays.append(current_date)
        current_date += timedelta(days=1)
    return sundays

file_path = r"C:\Users\coope\OneDrive\Desktop\broadway_ml\database\broadway_league_data.csv"

if os.path.exists(file_path): # starting with partially scrubbed data
    old_data = pd.read_csv(file_path)
    dates = []
    former_date = pd.to_datetime(old_data['Week End']).max().date()
    initial_date = former_date + timedelta(days=7)
else: # starting from scratch:
    # Note, since the first year of the page's data is fairly sparse, beginning in the 
    # middle of the year 1979, I set the very first start and end dates to be the first 
    # Sunday of 1979, and the last Sunday of 1979, respectively:
    dates = [("1/7/1979", "12/30/1979")]
    initial_date = date(1980, 6, 8)

# Then I add the remaining sundays from my added starting date (starting from the first to contain 
# data in 1980 for the 'from scratch' version) to present as tuples to be entered as strings using 
# a function to find all of the sundays.
if initial_date > date.today():
    sys.exit("Your CSV is up to date - the most recent week in your csv is the most recent week on BWL")
else:
    for sunday in all_sundays_between(initial_date, date.today()):
        sun_string = sunday.strftime("%m/%d/%Y")
        dates.append((sun_string, sun_string))

# Now onto working with the driver itself:
# First I get my driver up and running & go to the Broadway League's webpage...
chrome_driver_path = r"C:\Users\coope\OneDrive\Desktop\broadway_ml\data_collection\chromedriver.exe"
service = Service(executable_path = chrome_driver_path)
driver = webdriver.Chrome(service = service)
driver.get("https://www.broadwayleague.com/research/grosses-broadway-nyc/#weekly_grosses")

# Next, before I touch the data in the tables at all, I first get the headers to
# initialize a pandas dataframe in which to store the data as I encounter it.
table_head = WebDriverWait(driver, 5).until(EC.presence_of_element_located(
        (By.CSS_SELECTOR, "table#DataTables_Table_0 > thead"))
        )
headers = [th.text for th in table_head.find_elements(By.TAG_NAME, "th")]
full_bw_table = pd.DataFrame(columns=headers)

# Once I make it to the webpage successfully, and initialize my table's headers, I loop the 
# following steps for each date pair I have in my constructed dates list:
# 1) Wait for the page to load enough such that the search box is accessable, and click on it.
# 2) Wait for the start & end date textboxes to be accessable on the page
# 3) Enter the current tuple's start date in the start box, and its end date in the end box.
# 4) Wait for the search button to be clickable, and Click the Search Button
# 5) Wait for the table length selector to be accessable & Set the length of visible table to be 100
# 6) Wait for the table body to be accessable, and make it a variable using the driver
# 7) Add the data inside row by row to my dataframe (or other storage system later?)

for week in dates:
    # To keep track of which query we are on:
    print(f"Query Number: {dates.index(week)} / {len(dates)}")
    
    # Step 1)
    search_bar = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.CLASS_NAME, "search-box")))
    search_bar.click()

    # Step 2)
    start_box = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.NAME, "start_week_date")))
    end_box = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.NAME, "end_week_date")))

    # Step 3)
    start_box.clear()
    start_box.send_keys(week[0])
    end_box.clear()
    end_box.send_keys(week[1])

    # Step 4)
    button_selector = "input.subit[type='submit'][value*='Search NYC'][value*='Grosses']"
    search_button = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.CSS_SELECTOR, button_selector)))
    search_button.click()

    try: # in case the table doesn't show up at all,
        # Step 5) - had issues with loading times, so I manually...
        # ...wait for table to finish reloading after search;
        WebDriverWait(driver, 5).until(
            EC.invisibility_of_element_located((By.CSS_SELECTOR, "#DataTables_Table_0_processing"))
        )
        
        # re-locate the length selector after table refresh;
        time.sleep(0.20)
        select_element = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.NAME, "DataTables_Table_0_length"))
            )
        
        # create a new Select instance with fresh element reference;
        time.sleep(0.20)
        select = Select(select_element)
        select.select_by_value('100')
        
        # and finally Wait for table to finish reloading after length change;
        WebDriverWait(driver, 5).until(
            EC.invisibility_of_element_located((By.CSS_SELECTOR, "#DataTables_Table_0_processing"))
        )
    except:
        print("Issue Selecting Table Length / no table?")

    try:
        # Step 6)
        table_body = WebDriverWait(driver, 5).until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, "table#DataTables_Table_0 > tbody"))
            )
    except:
        print("Issue Accessing table body / no table?")
        
    try:
        # Step 7)
        rows = table_body.find_elements(By.TAG_NAME, "tr")
        for row in rows:
            cells = row.find_elements(By.TAG_NAME, "td")
            full_bw_table.loc[len(full_bw_table)] = [cell.text for cell in cells]

        print(f"Added {len(full_bw_table)} rows")
    except:
        print(f"Issues with week {week[0]}")
        continue

time.sleep(5)
try:
  driver.quit()
except:
  print("Driver Quit Issue")

print(full_bw_table.head())

if os.path.exists(file_path): # starting with partially scrubbed data
    new_data = BWL_reformat(full_bw_table)
    total_data = pd.concat([old_data, new_data], ignore_index=True, axis=0)
    total_data.to_csv(file_path, mode='w', index=False)
else: # starting from scratch:
    final_data = BWL_reformat(full_bw_table)
    final_data.to_csv(file_path)