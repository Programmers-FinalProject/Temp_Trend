from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, NoSuchElementException

import time
import random
from datetime import datetime
import pandas as pd
import csv

import boto3
import os

# ChromeDriverManager를 사용하여 ChromeDriver 자동 설치 및 설정
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)


def log_error(message):
    print(f"Error: {message}")

# 현재 시간 반환 함수
def current_time():
    return datetime.now().strftime("%Y%m%d%H%M")

# CSV 파일에 데이터를 저장하는 함수
def save_to_csv(data, filename):
    fieldnames = ["PRODUCT_NAME", "PRODUCT_LINK", "PRODUCT_IMG_LINK", "RANK", "DATETIME", "CREATE_TIME", "CATEGORY", "PRICE", "GENDER"]
    try:
        with open(filename, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            # 파일이 비어있으면 헤더 추가
            if file.tell() == 0:
                writer.writeheader()
            writer.writerows(data)
    except Exception as e:
        print(f"CSV 파일 저장 중 오류가 발생했습니다: {e}")

# 성별 변환 함수
def transform_gender(gender):
    if gender == "남성":
        return "men"
    elif gender == "여성":
        return "women"
    else : 
        pass


# 동일한 PRODUCT_NAME을 가진 항목들을 그룹화하여 GENDER 값 변경
def update_gender(group):
    if set(group['GENDER']) == {"men", "women"}:
        group['GENDER'] = "unisex"
    return group

LOCAL_FILE_PATH=f'../airflow/data/29cm_crawling_{current_time()[:8]}.csv'
AWS_ACCESS_KEY_ID = 'AKIA4RRVVY552CJHO5H4'
AWS_SECRET_ACCESS_KEY = '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'
S3_BUCKET_NAME = 'team-hori-1-bucket'

def upload_to_s3():
    s3_client = boto3.client('s3',
                             aws_access_key_id=AWS_ACCESS_KEY_ID,
                             aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                             region_name = "ap-northeast-2"
                             )
    s3_client.upload_file(LOCAL_FILE_PATH,S3_BUCKET_NAME,'crawling/29cm_crawling.csv')
    os.remove(f'{LOCAL_FILE_PATH}')
    print("Done")



upload_to_s3()


# try:
#     # 1. 29cm 홈페이지에 접속
#     driver.get("https://www.29cm.co.kr/home/")
#     WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '/html/body/home-root/div/ruler-gnb/div/div[3]/div/ul/li[1]/a')))
# except Exception as e:
#     log_error(f"29cm 홈페이지에 접속하는 중 문제가 발생했습니다: {e}")
#     driver.quit()
#     exit()

# try:
#     # 2. BEST 카테고리 버튼 클릭
#     best_button = driver.find_element(By.XPATH, '/html/body/home-root/div/ruler-gnb/div/div[3]/div/ul/li[1]/a')
#     best_button.click()
#     WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, '//*[@id="__next"]/div[4]/div[1]/div/ul/ul/li[1]/a')))
# except Exception as e:
#     log_error(f"BEST 카테고리 페이지 로드 중 문제가 발생했습니다: {e}")
#     driver.quit()
#     exit()

# # 3. BEST 카테고리 웹페이지의 각 카테고리 순회 및 접속
# categories = [
#     {"name": "여성의류", "xpath": '//*[@id="__next"]/div[4]/div[1]/div/ul/ul/li[1]/a'},
#     {"name": "여성가방", "xpath": '//*[@id="__next"]/div[4]/div[1]/div/ul/ul/li[2]/a'},
#     {"name": "여성신발", "xpath": '//*[@id="__next"]/div[4]/div[1]/div/ul/ul/li[3]/a'},
#     {"name": "여성액세서리", "xpath": '//*[@id="__next"]/div[4]/div[1]/div/ul/ul/li[4]/a'},
#     {"name": "남성의류", "xpath": '//*[@id="__next"]/div[4]/div[1]/div/ul/ul/li[5]/a'},
#     {"name": "남성가방", "xpath": '//*[@id="__next"]/div[4]/div[1]/div/ul/ul/li[6]/a'},
#     {"name": "남성신발", "xpath": '//*[@id="__next"]/div[4]/div[1]/div/ul/ul/li[7]/a'},
#     {"name": "남성악세서리", "xpath": '//*[@id="__next"]/div[4]/div[1]/div/ul/ul/li[8]/a'}
# ]

# # 데이터 저장 리스트
# data = []

# for category in categories:
#     try:
#         category_element = driver.find_element(By.XPATH, category["xpath"])
#         category_element.click()
#         WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, '//*[@id="__next"]/div[4]/div[2]/div[1]/ul/span[2]/label')))
#     except Exception as e:
#         log_error(f"카테고리 페이지 로드 중 문제가 발생했습니다: {e}")
#         driver.quit()
#         exit()

#     # 4. 하위 카테고리 순회 및 접속
#     try:
#         subcategories = driver.find_elements(By.XPATH, '//*[@id="__next"]/div[4]/div[2]/div[1]/ul/span/label')[1:]  # 첫 번째 요소(전체 카테고리) 제외
#         for subcategory in subcategories:
#             try:
#                 category_label = subcategory.text # category 속성 가져오기.
#                 subcategory.click()
#                 # 페이지 로딩 대기
#                 try:
#                     WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, '//*[@id="__next"]/div[4]/div[2]/ul/li[1]/div')))
#                 except TimeoutException:
#                     print("페이지 로딩이 너무 오래 걸립니다.")
#                     continue

#                 try:
#                     daily_button = driver.find_element(By.XPATH,'//*[@id="__next"]/div[4]/div[2]/div[2]/span[2]/label')
#                     daily_button.click()
#                     WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, '//*[@id="__next"]/div[4]/div[2]/ul/li[1]/div')))
#                 except Exception as e:
#                     log_error(f"일간 BEST 페이지 로드 중 문제가 발생했습니다: {e}")
#                     driver.quit()
#                     exit()
                
#                 time.sleep(random.uniform(2, 5))  # 랜덤 대기 시간

#                 # 인기 상품 상위 10개 정보 추출
#                 for i in range(1, 11):
#                     try: 
#                         product_xpath = f'//*[@id="__next"]/div[4]/div[2]/ul/li[{i}]/div'
#                         product_element = driver.find_element(By.XPATH, product_xpath)

#                         # 제품 이름 및 링크
#                         product_link_element = product_element.find_element(By.XPATH, './/a')
#                         product_link = product_link_element.get_attribute('href') # href 속성 가져오기
#                         product_name = product_link_element.get_attribute('title') # title 정보 가져오기
                        
#                         # 이미지 링크
#                         product_image_element = product_element.find_element(By.XPATH, './/img')
#                         product_image_link = product_image_element.get_attribute('src') # src 속성 가져오기
                        
#                         try:
#                             # 할인이 있는 상품의 가격 strong 태그 찾기
#                             original_price_element = product_element.find_element(By.XPATH, './/div/a/div/div/strong[contains(@class, "css-746sl9 e1pdz5yq7")]')
#                             original_price = original_price_element.text
#                             discounted_price_element = product_element.find_element(By.XPATH, './/div/a/div/div/strong[contains(@class, "css-746sl9 e1pdz5yq7")]/following-sibling::div/strong[contains(@class, "css-120pfho e1pdz5yq9")]')
#                             discounted_price = discounted_price_element.text
#                             # product_price = None  # 할인이 있는 경우에는 product_price를 사용하지 않음
#                             product_price = discounted_price
#                         except NoSuchElementException:
#                             try:
#                                 # 할인이 없는 상품의 가격 strong 태그 찾기
#                                 original_price_element = product_element.find_element(By.XPATH, './/div/a/div/div/strong[contains(@class, "css-txmkpj e1pdz5yq7")]')
#                                 product_price = original_price_element.text
#                                 original_price = None  # 할인이 없는 경우에는 original_price를 사용하지 않음
#                                 discounted_price = None  # 할인이 없는 경우에는 discounted_price를 사용하지 않음
#                             except NoSuchElementException:
#                                 try:
#                                     # 품절인 상품의 가격 strong 태그 찾기 (할인이 없는 경우)
#                                     sold_out_price_element = product_element.find_element(By.XPATH, './/div/a/div/div/strong[contains(@class, "css-19hhjvu e1pdz5yq7")]')
#                                     sold_out_price = sold_out_price_element.text
#                                     product_price = sold_out_price
#                                     original_price = None
#                                     discounted_price = None
#                                 except NoSuchElementException:
#                                     try:
#                                         # 품절인 상품의 가격 strong 태그 찾기 (할인이 있는 경우)
#                                         # <strong class="css-1xnq6we e1pdz5yq9">100,130</strong>
#                                         sold_out_discounted_price_element = product_element.find_element(By.XPATH, './/div/a/div/div/div/strong[contains(@class, "css-1xnq6we e1pdz5yq9")]')
#                                         sold_out_discounted_price = sold_out_discounted_price_element.text
#                                         product_price = sold_out_discounted_price
#                                         original_price = None
#                                         discounted_price = None
#                                     except NoSuchElementException as e:
#                                         log_error(f"가격 정보를 추출하는 중 문제가 발생했습니다: {e}")
#                                         product_price = None
#                                         original_price = None
#                                         discounted_price = None

#                         item = {
#                             "PRODUCT_NAME": product_name,
#                             "PRODUCT_LINK": product_link,
#                             "PRODUCT_IMG_LINK": product_image_link,
#                             "RANK": i,
#                             "DATETIME": current_time()[:8],
#                             "CREATE_TIME": current_time()[:8],
#                             "CATEGORY": f"{category['name']}_{category_label}" if category_label == 'EXCLUSIVE' else category_label,
#                             "PRICE": product_price if product_price else "NULL",
#                             "GENDER": transform_gender(category["name"][:2])
#                         }
#                         data.append(item)
#                     except Exception as e:
#                         log_error(f"인기 상품 {i} 정보를 추출하는 중 문제가 발생했습니다: {e}")
#             except Exception as e:
#                 log_error(f"하위 카테고리 클릭 중 문제가 발생했습니다: {e}")
#     except Exception as e:
#         log_error(f"하위 카테고리를 찾는 중 문제가 발생했습니다: {e}")

# driver.quit()

# # Data -> DataFrame 으로 변환
# df = pd.DataFrame(data)

# # 동일한 성별에 대해 
# # df = df.groupby('PRODUCT_NAME').apply(update_gender)

# # PRODUCT_NAME, CATEGORY, RANK, GENDER 기준으로 정렬
# df = df.sort_values(by=["CATEGORY", "GENDER","RANK"])


# # CSV 파일로 저장
# save_to_csv(df.to_dict('records'), LOCAL_FILE_PATH)

