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
service = Service(executable_path = "chromdriver.exe")
driver = webdriver.Chrome(service = service)
driver.get("https://www.broadwayleague.com/research/grosses-broadway-nyc/#weekly_grosses")
#... waiting for the page to load enough so I can move forward:
WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, "search")))
search_bar = driver.find_element(By.ID, "search")
search_bar.click()

# ********* PUT AFTER THE SEARCH SITUATION ******************************************************************************
# Next, I set the length of the table to be the longest it can be from its
# drop-down menue - 100 - to ensure all data from that week is shown.
##WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.NAME, "DataTables_Table_0_length")))
##select_element = driver.find_element(By.NAME, "DataTables_Table_0_length")
##select = Select(select_element)
##select.select_by_value('100')
# ***********************************************************************************************************************

# def select_week(driver, target_date, is_start_date=True):
#     """Selects a specific Sunday date in the calendar pop-up"""
#     # Determine which field to click (start or end)
#     field_id = "startDate" if is_start_date else "endDate"
    
#     try:
#         # Click the date field to open the calendar pop-up
#         date_field = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, field_id)))
#         ActionChains(driver).move_to_element(date_field).click().perform()
#         time.sleep(1)  # Allow calendar to open
        
#         # Convert target_date to datetime
#         target = datetime.strptime(target_date, "%m/%d/%Y")
        
#         # Navigate to target month/year
#         while True:
#             current_month_year = driver.find_element(
#                 By.CSS_SELECTOR, "div.ui-datepicker-title").text
#             target_month_year = target.strftime("%B %Y")
            
#             if current_month_year == target_month_year:
#                 break
                
#             # Determine navigation direction
#             current_date = datetime.strptime(current_month_year, "%B %Y")
#             nav_button = driver.find_element(
#                 By.CSS_SELECTOR, 
#                 "a.ui-datepicker-next" if current_date < target 
#                 else "a.ui-datepicker-prev"
#             )
#             ActionChains(driver).move_to_element(nav_button).click().perform()
#             time.sleep(0.5)
        
#         # Select the specific Sunday
#         sunday_cell = driver.find_element(
#             By.XPATH, 
#             f"//td[contains(@class, 'ui-datepicker-week-end')]//a[text()='{target.day}']"
#         )
#         ActionChains(driver).move_to_element(sunday_cell).click().perform()
#         time.sleep(1)
        
#     except Exception as e:
#         print(f"Error selecting date {target_date}: {str(e)}")
#         raise