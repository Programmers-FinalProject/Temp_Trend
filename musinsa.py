import selenium
from selenium import webdriver as wd
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time
import pandas as pd
from bs4 import BeautifulSoup
import requests
from itertools import repeat
import re

driver = wd.Chrome(service=Service(ChromeDriverManager().install()), options=wd.ChromeOptions())
driver.get("https://www.musinsa.com/categories/item/001?device=mw")
driver.implicitly_wait(3)
#이미지 링크
for i in range(1, 4):
    for j in range(1, 4):
        item = driver.find_element(By.XPATH, '//*[@id="root"]/main/div/section[3]/div[1]/div/div[{}]/div[{}]/div[2]/a[2]'.format(i, j)).text
        link = driver.find_element(By.XPATH, '//*[@id="root"]/main/div/section[3]/div[1]/div/div[{}]/div[{}]/div[2]/a[2]'.format(i, j)).get_attribute("href")
        img = driver.find_element(By.XPATH, '//*[@id="root"]/main/div/section[3]/div[1]/div/div[{}]/div[{}]/div[1]/figure/div/img'.format(i, j)).get_attribute("src") 
        driver.implicitly_wait(3)
driver.close()
