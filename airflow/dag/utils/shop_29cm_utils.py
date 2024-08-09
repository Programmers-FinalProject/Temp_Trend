# 성별 변환 함수
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from datetime import datetime
import json
import requests
from bs4 import BeautifulSoup
import boto3
import logging

from airflow.models import Variable

def transform_gender(gender):
    if gender == "남성":
        return "men"
    elif gender == "여성":
        return "women"
    else:
        return "unisex"
    
def fetch_product_links(category,):
    # Selenium을 사용하여 상품 링크 수집
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    product_data = []
    etl_time = datetime.now().strftime("%Y-%m-%d")
    
    try:
        driver.get("https://www.29cm.co.kr/home/")
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, '/html/body/home-root/div/ruler-gnb/div/div[3]/div/ul/li[1]/a')))
        
        best_button = driver.find_element(By.XPATH, '/html/body/home-root/div/ruler-gnb/div/div[3]/div/ul/li[1]/a')
        best_button.click()
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, '//*[@id="__next"]/div[4]/div[1]/div/ul/ul/li[8]/a')))
        
        category = category
        category_element = driver.find_element(By.XPATH, category["xpath"])
        category_element.click()
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, '//*[@id="__next"]/div[4]/div[2]/div[1]/ul/span[2]/label')))
        
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, '//*[@id="__next"]/div[4]/div[2]/div[2]/span[2]/label')))
        daily_btn = driver.find_element(By.XPATH, '//*[@id="__next"]/div[4]/div[2]/div[2]/span[2]/label')
        daily_btn.click()
        
        subcategories = driver.find_elements(By.XPATH, '//*[@id="__next"]/div[4]/div[2]/div[1]/ul/span/label')[1:]
        
        for subcategory in subcategories:
            subcategory.click()
            WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, '//*[@id="__next"]/div[4]/div[2]/ul/li[1]/div')))
            for i in range(1, 11):
                product_xpath = f'//*[@id="__next"]/div[4]/div[2]/ul/li[{i}]/div'
                product_element = driver.find_element(By.XPATH, product_xpath)
                
                # 상품 링크
                product_link_element = product_element.find_element(By.XPATH, './/a')
                product_link = product_link_element.get_attribute('href')

                # 상품 이름
                product_name = product_link_element.get_attribute('title') # title 정보 가져오기

                # 이미지 링크
                product_image_element = product_element.find_element(By.XPATH, './/img')
                product_image_link = product_image_element.get_attribute('src')  # src 속성 가져오기

                price = None
                
                # 할인 가격 Xpath
                discount_price_xpath = f'//*[@id="__next"]/div[4]/div[2]/ul/li[{i}]/div/div/a[2]/div/div/div/strong'
                # 정가 Xpath
                regular_price_xpath = f'//*[@id="__next"]/div[4]/div[2]/ul/li[{i}]/div/div/a[2]/div/div/strong'

                try:
                    # 할인 가격이 존재하는지 확인
                    discount_price_element = driver.find_element(By.XPATH, discount_price_xpath)
                    price = discount_price_element.text.strip()  # 할인가격
                except:
                    # 할인 가격이 없다면 정가를 시도
                    try:
                        regular_price_element = driver.find_element(By.XPATH, regular_price_xpath)
                        price = regular_price_element.text.strip()  # 정가
                    except:
                        price = "가격 정보 없음"
                
                # 카테고리 정보 추가
                product_data.append({
                    "product_name": product_name,
                    "product_link": product_link,
                    "image_link": product_image_link,
                    "rank":i,
                    "date": etl_time,
                    "data_creation_time": etl_time,
                    "category1": None,
                    "category2": None,
                    "category3": None,
                    "price": price,
                    "gender": transform_gender(category['name'][:2])
                })

    except Exception as e:
        print(f"상품 링크 수집 중 오류: {e}")
    finally:
        driver.quit()
    
    return json.dumps(product_data)

def fetch_product_info(product_data):
    logger = logging.getLogger(__name__)
    if isinstance(product_data, str):
        try:
            product_data = json.loads(product_data)  # JSON 문자열을 파싱
        except json.JSONDecodeError as e:
            logger.info(f"JSON 파싱 오류: {e}")
    
    for product in product_data:
        product_link = product["product_link"]
        try:
            response = requests.get(product_link)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                script_tags = soup.find_all('script')

                json_data = None
                for script in script_tags:
                    if 'frontCategoryInfo' in script.text:
                        json_data = script.string
                        break
                
                if json_data:
                    # JSON 데이터 파싱
                    json_data = json_data[json_data.index('{'):json_data.rindex('}')+1]  # JSON 부분만 잘라내기
                    data = json.loads(json_data)

                    # 카테고리 정보 추출
                    front_category_info = data.get('props', {}).get('pageProps', {}).get('dehydratedState', {}).get('queries', [{}])[0].get('state', {}).get('data', {}).get('frontCategoryInfo', [])

                    # 카테고리 수집
                    if front_category_info:
                        # product_link에서 category_large_code 추출
                        large_code = product_link.split('category_large_code=')[-1]
                        large_code = large_code.split('&')[0]  # '&'가 있을 경우 분리

                        # 해당 large_code와 일치하는 카테고리 찾기
                        category = next((cat for cat in front_category_info if str(cat['category1Code']) == large_code), None)

                        if category:
                            product["category1"] = category.get('category1Name') or "None"
                            product["category2"] = category.get('category2Name') or "None"
                            product["category3"] = category.get('category3Name') or "None"
                        else:
                            product["category1"] = '없음'
                            product["category2"] = '없음'
                            product["category3"] = '없음'
                    else:
                        print("카테고리 정보를 찾을 수 없습니다.")
                        return None

                        # print(f"카테고리: {category1_name} > {category2_name} > {category3_name}")
        except Exception as e:
            print(f"상품 정보 수집 중 오류: {e}")
            return None
    return json.dumps(product_data)

def result_save_to_dir(product_data):
    import pandas as pd 
    logger = logging.getLogger(__name__)
    if isinstance(product_data, str):
        try:
            product_data = json.loads(product_data)  # JSON 문자열을 파싱
        except json.JSONDecodeError as e:
            logger.info(f"JSON 파싱 오류: {e}")
        
    df = pd.DataFrame(product_data)
    category_name = df['category1'].unique()[0]
    etl_time = datetime.now().strftime("%Y%m%d")

    file_name = f"29cm_{category_name}_{etl_time}.csv"
    local_file_path = f"/opt/airflow/data/{file_name}"

    # CSV 파일로 저장
    df.to_csv(local_file_path, index=False, encoding='utf-8-sig')
    
    # S3에 업로드
    
    BUCKET_NAME = Variable.get('s3_bucket')
    AWS_ACCESS_KEY_ID = Variable.get('ACCESS_KEY')
    AWS_SECRET_ACCESS_KEY = Variable.get('SECRET_KEY')
    s3_client = boto3.client('s3',
                             aws_access_key_id=AWS_ACCESS_KEY_ID,
                             aws_secret_access_key=AWS_SECRET_ACCESS_KEY
                             )
    s3_client.upload_file(local_file_path, BUCKET_NAME, f'crawling/{file_name}')

