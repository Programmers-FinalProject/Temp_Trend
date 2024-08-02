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
   
def fetch_data():
    data = []
    chrome_options=wd.ChromeOptions()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('user_agent = Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36')
    driver = wd.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    item_codes = ['001001', '001002', '001003', '001004', '001005', '001006', '001010', '001013', '001011',
                '002003', '002002', '002018', '002009', '002006', '002007', '002012', '002001', '002017',
                '002016', '002019', '002014', '002024', '002020', '002004', '002013', '002021', '002022',
                '002008', '002023', '002025', '003002', '003004', '003009', '003007', '003011', '003008',
                '003005', '003010', '020008', '020007', '020006', '022001', '022002', '022003', '018002',
                '018003', '018001', '005014', '005004', '005019', '005012', '005018', '005015', '005017',
                '005016', '005011']
    now = time.strftime("%Y-%m-%d", time.gmtime())
    for item_code in item_codes:
        driver.get(f"https://www.musinsa.com/categories/item/{item_code}?device=mw")
        driver.implicitly_wait(10)
        for i in range(1, 4):
            for j in range(1, 4):
                rank = (i - 1) * 3 + j
                item = driver.find_element(By.XPATH, f'/html/body/div[1]/div/main/div/section[3]/div[1]/div/div[{i}]/div[{j}]/div[2]/a[2]').text
                link = driver.find_element(By.XPATH, f'/html/body/div[1]/div/main/div/section[3]/div[1]/div/div[{i}]/div[{j}]/div[2]/a[2]').get_attribute("href")
                img = driver.find_element(By.XPATH, f'/html/body/div[1]/div/main/div/section[3]/div[1]/div/div[{i}]/div[{j}]/div[1]/figure/div/img').get_attribute("src")
                price = driver.find_element(By.XPATH, f'/html/body/div[1]/div/main/div/section[3]/div[1]/div/div[{i}]/div[{j}]/div[2]/div/div[1]/div/div/div/span').text
                category = driver.find_element(By.CLASS_NAME, 'category__sc-lccsha-1.BVycB').text
                item_element = driver.find_element(By.XPATH, f'/html/body/div[1]/div/main/div/section[3]/div[1]/div/div[{i}]/div[{j}]/div[2]/a[2]')
                item_element.send_keys(Keys.ENTER)
                driver.implicitly_wait(10)
                genders = driver.find_elements(By.CLASS_NAME, 'sc-18j0po5-5.fPhtQs')
                for g in genders:
                    if g.text == '남성, 여성':
                        gender = 'unisex'
                    elif g.text == '남성':
                        gender = 'm'
                    elif g.text == '여성':
                        gender = 'w'
                driver.get(f"https://www.musinsa.com/categories/item/{item_code}?device=mw")
                driver.implicitly_wait(10)
                print(item_code + f' :{rank}')
                data.append({
                    'PRODUCT_NAME': item,
                    'PRODUCT_LINK': link, 
                    'PRODUCT_IMG_LINK': img, 
                    'RANK': rank, 
                    'DATETIME': now, 
                    'CREATE_TIME': now, 
                    'CATEGORY': category, 
                    'PRICE': price, 
                    'GENDER': gender
                })
    driver.implicitly_wait(10)
    driver.close()
    return data

def data_to_csv(**kwargs):
    ti = kwargs['ti']
    data = ti.xcom_pull(task_ids='fetch_data')
    df = pd.DataFrame(data)
    csv_buffer = StringIO()
    df.to_csv(csv_buffer, index=False)
    ti.xcom_push(key='csv_buffer', value=csv_buffer.getvalue())

def upload_to_s3(**kwargs):
    ti = kwargs['ti']
    csv_data = ti.xcom_pull(task_ids='data_to_csv', key='csv_buffer')

    s3_client = boto3.client(
        's3',
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY
        )
    s3_client.put_object(Bucket=S3_BUCKET_NAME, Key=FILE_KEY, Body=csv_data)

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2024, 1, 1),
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

data_to_csv_task = PythonOperator(
    task_id='data_to_csv',
    python_callable=data_to_csv,
    provide_context=True,
    dag=dag,
)

upload_to_s3_task = PythonOperator(
    task_id='upload_to_s3',
    python_callable=upload_to_s3,
    provide_context=True,
    dag=dag,
)

fetch_data_task >> data_to_csv_task >> upload_to_s3_task