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
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
from airflow.models import Variable
import pandas as pd
import boto3
import os

S3_BUCKET_NAME = 'team-hori-1-bucket'
S3_KEY = 'musinsa.csv'
AWS_ACCESS_KEY_ID = Variable.get('ACCESS_KEY')
AWS_SECRET_ACCESS_KEY = Variable.get('SECRET_KEY')
LOCAL_FILE_PATH = '/tmp/data.csv'

def fetch_data():
    data = []
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
                        print("상품링크 " + link)
                        print("이미지링크 " + img)
                        print("순위 " + str(rank))
                        print("날짜 " + now)
                        print("데이터생성일 " + now)
                        print("카테고리 " + category)
                        print("가격 "+ price)
                        print("성별 " + gender)
                        data.append({
                            'PRODUCT_NAME': item,
                            'PRODUCT_LINK': link, 
                            'PRODUCT_IMG_LINK': img, 
                            'RANK': rank, 
                            'DATETIME': now, 
                            'CREATE_TIME': now, 
                            'CATEGORY': category, 
                            'PRICE': price, 
                            'GENDER':gender
                            })
                        driver.implicitly_wait(5)
                        driver.back()
                        col.send_keys(Keys.ENTER)
                        driver.implicitly_wait(5)
                driver.back()
                driver.implicitly_wait(5)
            driver.implicitly_wait(5)
    driver.close()
    df = pd.DataFrame(data)
    df.to_csv(LOCAL_FILE_PATH, index=False)

def upload_to_s3():
    s3_client = boto3.client(
        's3',
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY
    )
    s3_client.upload_file(LOCAL_FILE_PATH, S3_BUCKET_NAME, S3_KEY)
    os.remove(LOCAL_FILE_PATH)

default_args = {
    'start_date': days_ago(1),
    'retries': 1,
}

dag = DAG(
    dag_id ='musinsa_crawl_and_upload_to_s3',
    default_args=default_args,
    description='Crawl data and upload to S3',
    schedule_interval='@daily',
)
fetch_data_task = PythonOperator(
    task_id='fetch_data',
    python_callable=fetch_data,
    dag=dag,
)

upload_to_s3_task = PythonOperator(
    task_id='upload_to_s3',
    python_callable=upload_to_s3,
    dag=dag,
)

fetch_data_task >> upload_to_s3_task