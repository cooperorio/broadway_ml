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

file_path = r"C:\Users\coope\OneDrive\Desktop\broadway_ml\database\broadway_league_data.csv"

pre_data = pd.read_csv(file_path)

print(pre_data.head())
post_data = BWL_reformat(pre_data)
post_data.to_csv(file_path, mode='w', index=False)