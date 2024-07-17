import selenium
from selenium import webdriver as wd
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import pandas as pd
from bs4 import BeautifulSoup
import requests
from itertools import repeat

driver = wd.Chrome(service=Service(ChromeDriverManager().install()), options=wd.ChromeOptions())
driver.get("https://www.musinsa.com/dp/menu")
driver.implicitly_wait(5)
now = time.strftime("%Y-%m-%d", time.gmtime())
for r in range(1, 8):
    rows = driver.find_elements(By.XPATH, '/html/body/div[1]/div/main/section[2]/article[2]/article[{}]/article'.format(r))
    for rowIndex, row in enumerate(rows):
        cols = driver.find_elements(By.XPATH, '/html/body/div[1]/div/main/section[2]/article[2]/article[{}]/article[{}]/div/a'.format(r, rowIndex + 1))
        for colIndex, col in enumerate(cols[2:]):
            category = driver.find_element(By.XPATH, '/html/body/div[1]/div/main/section[2]/article[2]/article[{}]/article[{}]/div/a[{}]/span'.format(r, rowIndex + 1, colIndex + 3)).text
            col.send_keys(Keys.ENTER)
            driver.implicitly_wait(5)
            #성별
            for i in range(1, 4):
                for j in range(1, 4):
                    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.ID, 'root')))
                    rank = (i - 1) * 3 + j
                    item = driver.find_element(By.XPATH, '/html/body/div[1]/div/main/div/section[3]/div[1]/div/div[{}]/div[{}]/div[2]/a[2]'.format(i, j)).text
                    link = driver.find_element(By.XPATH, '/html/body/div[1]/div/main/div/section[3]/div[1]/div/div[{}]/div[{}]/div[2]/a[2]'.format(i, j)).get_attribute("href")
                    img = driver.find_element(By.XPATH, '/html/body/div[1]/div/main/div/section[3]/div[1]/div/div[{}]/div[{}]/div[1]/figure/div/img'.format(i, j)).get_attribute("src")
                    price = driver.find_element(By.XPATH, '/html/body/div[1]/div/main/div/section[3]/div[1]/div/div[{}]/div[{}]/div[2]/div/div[1]/div/div/div/span'.format(i, j)).text
                    driver.find_element(By.XPATH, '/html/body/div[1]/div/main/div/section[3]/div[1]/div/div[{}]/div[{}]/div[2]/a[2]'.format(i, j)).send_keys(Keys.ENTER)
                    driver.implicitly_wait(5)
                    genders = driver.find_elements(By.CLASS_NAME, 'sc-18j0po5-5.fPhtQs')
                    for g in genders:
                        if g.text == '남성, 여성':
                            gender = 'unisex'
                        elif g.text == '남성':
                            gender = 'm'
                        elif g.text == '여성':
                            gender = 'w'
                    driver.back()
                    print("제품이름 " + item)
                    print("제품링크 " + link)
                    print("이미지링크 " + img)
                    print("순위 " + str(rank))
                    print("날짜 " + now)
                    print("생성일 " + now)
                    print("카테고리 " + category)
                    print("가격 "+ price)
                    print("성별 " + gender)
                    driver.implicitly_wait(5)
                    driver.back()
                    col.send_keys(Keys.ENTER)
                    driver.implicitly_wait(5)
            driver.back()
            driver.implicitly_wait(5)
        driver.implicitly_wait(5)
driver.close()
