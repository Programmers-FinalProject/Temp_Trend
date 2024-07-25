from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException,NoSuchElementException 

import pandas as pd
import boto3
from datetime import datetime
import io
import time  
import random 

from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.models import Variable  


# 환경변수 등록 필요
S3_BUCKET_NAME = Variable.get("S3_BUCKET_NAME")  
AWS_ACCESS_KEY_ID = Variable.get("ACCESS_KEY")  
AWS_SECRET_ACCESS_KEY = Variable.get("SECRET_KEY")  

def log_error(message):
    print(f"Error: {message}")

# 현재 시간 반환 함수
def current_time():
    return datetime.now().strftime("%Y%m%d%H%M")

# S3에 DataFrame을 CSV 형식으로 업로드
def upload_to_s3(dataframe):
    csv_buffer = io.StringIO()
    dataframe.to_csv(csv_buffer, index=False, encoding='utf-8')  # DataFrame을 CSV로 변환

    s3_client = boto3.client('s3',
                             aws_access_key_id=AWS_ACCESS_KEY_ID,
                             aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                             region_name="ap-northeast-2")
    s3_client.put_object(Bucket=S3_BUCKET_NAME, Key=f'crawling/29cm_crawling_{current_time()[:8]}.csv', Body=csv_buffer.getvalue())
    print("업로드 완료")

# 성별 변환 함수
def transform_gender(gender):
    if gender == "남성":
        return "men"
    elif gender == "여성":
        return "women"
    else:
        return "unisex"
        
def crawling_and_save_to_s3(): 
    # ChromeDriver 설정
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # 헤드리스 모드로 실행
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    # options.binary_location = "/opt/chrome/chrome"
    options.binary_location = "/usr/bin/chromium"  # Chromium의 경로

    # service = Service("/opt/chromedriver")
    service = Service("/usr/bin/chromedriver")
    driver = webdriver.Chrome(service=service, options=options)

    try:
        # 1. 29cm 홈페이지에 접속
        driver.get("https://www.29cm.co.kr/home/")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '/html/body/home-root/div/ruler-gnb/div/div[3]/div/ul/li[1]/a')))
        print("29cm 정상접속하였습니다.")
    except Exception as e:
        log_error(f"29cm 홈페이지에 접속하는 중 문제가 발생했습니다: {e}")
        driver.quit()
        exit()

    try:
        # 2. BEST 카테고리 버튼 클릭
        best_button = driver.find_element(By.XPATH, '/html/body/home-root/div/ruler-gnb/div/div[3]/div/ul/li[1]/a')
        best_button.click()
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, '//*[@id="__next"]/div[4]/div[1]/div/ul/ul/li[1]/a')))
        print("베스트 페이지에 정상접속 하였습니다..")
    except Exception as e:
        log_error(f"BEST 카테고리 페이지 로드 중 문제가 발생했습니다: {e}")
        driver.quit()
        exit()

    # 3. BEST 카테고리 웹페이지의 각 카테고리 순회 및 접속
    categories = [
        {"name": "여성의류", "xpath": '//*[@id="__next"]/div[4]/div[1]/div/ul/ul/li[1]/a'},
        {"name": "여성가방", "xpath": '//*[@id="__next"]/div[4]/div[1]/div/ul/ul/li[2]/a'},
        {"name": "여성신발", "xpath": '//*[@id="__next"]/div[4]/div[1]/div/ul/ul/li[3]/a'},
        {"name": "여성액세서리", "xpath": '//*[@id="__next"]/div[4]/div[1]/div/ul/ul/li[4]/a'},
        {"name": "남성의류", "xpath": '//*[@id="__next"]/div[4]/div[1]/div/ul/ul/li[5]/a'},
        {"name": "남성가방", "xpath": '//*[@id="__next"]/div[4]/div[1]/div/ul/ul/li[6]/a'},
        {"name": "남성신발", "xpath": '//*[@id="__next"]/div[4]/div[1]/div/ul/ul/li[7]/a'},
        {"name": "남성악세서리", "xpath": '//*[@id="__next"]/div[4]/div[1]/div/ul/ul/li[8]/a'}
        ]

    # 데이터 저장 리스트
    data = []

    for category in categories:
        try:
            category_element = driver.find_element(By.XPATH, category["xpath"])
            category_element.click()
            WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, '//*[@id="__next"]/div[4]/div[2]/div[1]/ul/span[2]/label')))
            print(f"{category['name']} 페이지에 정상접속 하였습니다.")
        except Exception as e:
            log_error(f"카테고리 페이지 로드 중 문제가 발생했습니다: {e}")
            driver.quit()
            exit()

        # 4. 하위 카테고리 순회 및 접속
        try:
            subcategories = driver.find_elements(By.XPATH, '//*[@id="__next"]/div[4]/div[2]/div[1]/ul/span/label')[1:]  # 첫 번째 요소 제외
            for subcategory in subcategories:
                try:
                    category_label = subcategory.text # category 속성 가져오기.
                    subcategory.click()
                    daily_button = driver.find_element(By.XPATH, '//*[@id="__next"]/div[4]/div[2]/div[2]/span[2]/label').click()
                    # 페이지 로딩 대기
                    try:
                        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, '//*[@id="__next"]/div[4]/div[2]/ul/li[1]/div')))
                    except TimeoutException:
                        print("페이지 로딩이 너무 오래 걸립니다.")
                        continue

                    time.sleep(random.uniform(2, 5))  # 랜덤 대기 시간
                    print(f'{category_label} 페이지에 정상 접속하였습니다.')

                    # 인기 상품 상위 10개 정보 추출
                    for i in range(1, 11):
                        try:
                            product_xpath = f'//*[@id="__next"]/div[4]/div[2]/ul/li[{i}]/div'
                            product_element = driver.find_element(By.XPATH, product_xpath)

                            # 제품 이름 및 링크
                            product_link_element = product_element.find_element(By.XPATH, './/a')
                            product_link = product_link_element.get_attribute('href') # href 속성 가져오기
                            product_name = product_link_element.get_attribute('title') # title 정보 가져오기

                            # 이미지 링크
                            product_image_element = product_element.find_element(By.XPATH, './/img')
                            product_image_link = product_image_element.get_attribute('src') # src 속성 가져오기

                            try:
                                # 할인이 있는 상품의 가격 strong 태그 찾기
                                original_price_element = product_element.find_element(By.XPATH, './/div/a/div/div/strong[contains(@class, "css-746sl9 e1pdz5yq7")]')
                                original_price = original_price_element.text
                                discounted_price_element = product_element.find_element(By.XPATH, './/div/a/div/div/strong[contains(@class, "css-746sl9 e1pdz5yq7")]/following-sibling::div/strong[contains(@class, "css-120pfho e1pdz5yq9")]')
                                discounted_price = discounted_price_element.text
                                # product_price = None  # 할인이 있는 경우에는 product_price를 사용하지 않음
                                product_price = discounted_price
                            except NoSuchElementException:
                                try:
                                    # 할인이 없는 상품의 가격 strong 태그 찾기
                                    original_price_element = product_element.find_element(By.XPATH, './/div/a/div/div/strong[contains(@class, "css-txmkpj e1pdz5yq7")]')
                                    product_price = original_price_element.text
                                    original_price = None  # 할인이 없는 경우에는 original_price를 사용하지 않음
                                    discounted_price = None  # 할인이 없는 경우에는 discounted_price를 사용하지 않음
                                except NoSuchElementException:
                                    try:
                                        # 품절인 상품의 가격 strong 태그 찾기 (할인이 없는 경우)
                                        sold_out_price_element = product_element.find_element(By.XPATH, './/div/a/div/div/strong[contains(@class, "css-19hhjvu e1pdz5yq7")]')
                                        sold_out_price = sold_out_price_element.text
                                        product_price = sold_out_price
                                        original_price = None
                                        discounted_price = None
                                    except NoSuchElementException:
                                        try:
                                            # 품절인 상품의 가격 strong 태그 찾기 (할인이 있는 경우)
                                            sold_out_discounted_price_element = product_element.find_element(By.XPATH, './/div/a/div/div/div/strong[contains(@class, "css-1xnq6we e1pdz5yq9")]')
                                            sold_out_discounted_price = sold_out_discounted_price_element.text
                                            product_price = sold_out_discounted_price
                                            original_price = None
                                            discounted_price = None
                                        except NoSuchElementException as e:
                                            log_error(f"가격 정보를 추출하는 중 문제가 발생했습니다: {e}")
                                            product_price = None
                                            original_price = None
                                            discounted_price = None

                            item = {
                                "PRODUCT_NAME": product_name,
                                "PRODUCT_LINK": product_link,
                                "PRODUCT_IMG_LINK": product_image_link,
                                "RANK": i,
                                "DATETIME": current_time()[:8],
                                "CREATE_TIME": current_time()[:8],
                                "CATEGORY": f'{category["name"]}_{category_label}' if category_label == "EXCLUSIVE" or category_label == "해외브랜드" else category_label,
                                "PRICE": product_price if product_price else "NULL",
                                "GENDER": transform_gender(category["name"][:2])
                            }
                            data.append(item)
                        except Exception as e:
                            log_error(f"인기 상품 {i} 정보를 추출하는 중 문제가 발생했습니다: {e}")
                except Exception as e:
                    log_error(f"하위 카테고리 클릭 중 문제가 발생했습니다: {e}")
        except Exception as e:
            log_error(f"하위 카테고리를 찾는 중 문제가 발생했습니다: {e}")

    driver.quit()
    
     # Data -> DataFrame으로 변환
    df = pd.DataFrame(data)
    df = df.sort_values(by=["CATEGORY", "GENDER", "RANK"])

    # S3에 업로드
    upload_to_s3(df)

# Airflow DAG 정의
default_args = {
    'owner': 'airflow',
    'start_date': datetime(2024, 7, 23),
    'retries': 1,
    'catchup': False,  # 이전 실행에 대한 백필 방지
}

dag = DAG(
    '29cm_crawling_dag',
    default_args=default_args,
    schedule_interval='0 23 * * *',  # 매일 저녁 11시에 실행
)

# PythonOperator를 사용하여 크롤링 작업을 태스크로 등록
crawling_task = PythonOperator(
    task_id='crawling_and_save_to_s3',
    python_callable=crawling_and_save_to_s3,
    dag=dag,
)

crawling_task