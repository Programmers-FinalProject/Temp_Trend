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
from airflow.models import Variable
import pandas as pd
import boto3
from datetime import datetime
import io

# S3 버킷 및 파일 설정
FILE_KEY = 'musinsa.csv'
S3_BUCKET_NAME = 'team-hori-1-bucket'
AWS_ACCESS_KEY_ID = Variable.get('ACCESS_KEY')
AWS_SECRET_ACCESS_KEY = Variable.get('SECRET_KEY')

try:
    s3_client = boto3.client(
        's3',
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
except Exception as e:
    print(e)
    raise
        
def fetch_data():
    data = []
    chrome_options=wd.ChromeOptions()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument("--single-process")
    remote_webdriver = 'remote_chromedriver'
    driver = wd.Remote(f'{remote_webdriver}:4444/wd/hub', options=chrome_options) 
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
                driver.implicitly_wait(20)
                #성별
                for i in range(1, 4):
                    for j in range(1, 4):
                        rank = (i - 1) * 3 + j
                        item = driver.find_element(By.XPATH, '/html/body/div[1]/div/main/div/section[3]/div[1]/div/div[{}]/div[{}]/div[2]/a[2]'.format(i, j)).text
                        link = driver.find_element(By.XPATH, '/html/body/div[1]/div/main/div/section[3]/div[1]/div/div[{}]/div[{}]/div[2]/a[2]'.format(i, j)).get_attribute("href")
                        img = driver.find_element(By.XPATH, '/html/body/div[1]/div/main/div/section[3]/div[1]/div/div[{}]/div[{}]/div[1]/figure/div/img'.format(i, j)).get_attribute("src")
                        price = driver.find_element(By.XPATH, '/html/body/div[1]/div/main/div/section[3]/div[1]/div/div[{}]/div[{}]/div[2]/div/div[1]/div/div/div/span'.format(i, j)).text
                        driver.find_element(By.XPATH, '/html/body/div[1]/div/main/div/section[3]/div[1]/div/div[{}]/div[{}]/div[2]/a[2]'.format(i, j)).send_keys(Keys.ENTER)
                        driver.implicitly_wait(20)
                        genders = driver.find_elements(By.CLASS_NAME, 'sc-18j0po5-5.fPhtQs')
                        for g in genders:
                            if g.text == '남성, 여성':
                                gender = 'unisex'
                            elif g.text == '남성':
                                gender = 'm'
                            elif g.text == '여성':
                                gender = 'w'
                        driver.back()
                        driver.implicitly_wait(20)
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
                        print("상품이름 "+item)
                        driver.back()
                        driver.implicitly_wait(20)
                        col.send_keys(Keys.ENTER)
                        driver.implicitly_wait(20)
                driver.back()
                driver.implicitly_wait(20)
            driver.implicitly_wait(20)
    driver.close()
    df = pd.DataFrame(data)
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)
    return csv_buffer.getvalue()

def upload_to_s3(**kwargs):
    csv_data = kwargs['ti'].xcom_pull(task_ids='create_new_csv')
    s3_client.put_object(Bucket=S3_BUCKET_NAME, Key=FILE_KEY, Body=csv_data)

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2023, 1, 1),
    'catchup' : False,
}

dag = DAG(
    dag_id ='musinsa_crawl_and_upload_to_s3',
    default_args=default_args,
    schedule_interval='@daily',
    max_active_runs=1,
)

fetch_data_task = PythonOperator(
    task_id='fetch_data',
    python_callable=fetch_data,
    provide_context=True,
    dag=dag,
)

upload_to_s3_task = PythonOperator(
    task_id='upload_to_s3',
    python_callable=upload_to_s3,
    provide_context=True,
    dag=dag,
)

fetch_data_task >> upload_to_s3_task