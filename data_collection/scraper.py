# Written by Cooper Orio for Broadway Data Project

#
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from datetime import datetime, timedelta
import time

# First I get my driver up and running & go to the Broadway League's webpage...
chrome_driver_path = r"C:\Users\coope\OneDrive\Desktop\broadway_ml\data_collection\chromedriver.exe"
service = Service(executable_path = chrome_driver_path)
driver = webdriver.Chrome(service = service)
driver.get("https://www.broadwayleague.com/research/grosses-broadway-nyc/#weekly_grosses")
#... waiting for the page to load enough so I can move forward:
WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, "search-box")))

# Next I click on the search bar in preparation for inputting the date range:
search_bar = driver.find_element(By.CLASS_NAME, "search-box")
search_bar.click()

time.sleep(10)

driver.quit()

# ********* PUT AFTER THE SEARCH SITUATION ******************************************************************************
# Next, I set the length of the table to be the longest it can be from its
# drop-down menue - 100 - to ensure all data from that week is shown.
##WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.NAME, "DataTables_Table_0_length")))
##select_element = driver.find_element(By.NAME, "DataTables_Table_0_length")
##select = Select(select_element)
##select.select_by_value('100')
# ***********************************************************************************************************************
