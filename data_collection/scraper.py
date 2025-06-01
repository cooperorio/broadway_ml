# Written by Cooper Orio for Broadway Data Project

# My Selenium imports, most of which will be used I think(?)
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from datetime import date, datetime, timedelta
import time

# Before doing any work with the driver I will use to scrub the website, I first
# make a list of start_date-end_date pairs to be entered into the search bar when
# we are able to query the page.

# Note, since the first year of the page's data is fairly sparse, beginning in the 
# middle of the year 1979, I set the very first start and end dates to be the first 
# Sunday of 1979, and the last Sunday of 1979, respectively:
dates = [("1/7/1979", "12/30/1979")]

# Then I add the remaining sundays from 1980 to present as tuples to be entered as strings
# using a function to find all of the sundays.
def all_sundays_between(start_date, end_date):
    sundays = []
    current_date = start_date
    while current_date <= end_date:
        if current_date.weekday() == 6:  # Sunday is represented by 6
            sundays.append(current_date)
        current_date += timedelta(days=1)
    return sundays

for sunday in all_sundays_between(date(1980, 1, 6), date.today()):
    sun_string = sunday.strftime("%m/%d/%Y")
    dates.append((sun_string, sun_string))


# Now, onto working with the actual driver:
# First I get my driver up and running & go to the Broadway League's webpage...
chrome_driver_path = r"C:\Users\coope\OneDrive\Desktop\broadway_ml\data_collection\chromedriver.exe"
service = Service(executable_path = chrome_driver_path)
driver = webdriver.Chrome(service = service)
driver.get("https://www.broadwayleague.com/research/grosses-broadway-nyc/#weekly_grosses")

# Once I make it to the webpage successfully, I loop the following steps 
# for each date pair I have in my constructed dates list:
# 1) Wait for the page to load enough such that the search box is accessable, and click on it.
# 2) Wait for the start & end date textboxes to be accessable on the page
# 3) Enter the current tuple's start date in the start box, and its end date in the end box.
# 4) Wait for the search button to be clickable, and Click the Search Button
# 5) Wait for the table with data to be present, and set the length of visible table to be 100
# 6) Add the data inside row by row to dataframe (or other storage system?)

for week in dates:
    # Step 1)
    WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.CLASS_NAME, "search-box")))
    search_bar = driver.find_element(By.CLASS_NAME, "search-box")
    search_bar.click()

    # Step 2)
    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.NAME, "start_week_date")))
    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.NAME, "end_week_date")))

    # Step 3)
    start_box = driver.find_element(By.NAME, "start_week_date")
    end_box = driver.find_element(By.NAME, "end_week_date")
    start_box.send_keys(week[0])
    end_box.send_keys(week[1])

    # Step 4)
    button_selector = "input.subit[type='submit'][value='Search NYC Grosses']"
    WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.CSS_SELECTOR, button_selector)))
    # ***Still need to make sure the above for the button works...***

    # Step 5)
    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.NAME, "DataTables_Table_0_length")))
    select_element = driver.find_element(By.NAME, "DataTables_Table_0_length")
    select = Select(select_element)
    select.select_by_value('100')

    # Step 6) **********************

time.sleep(10)

driver.quit()
