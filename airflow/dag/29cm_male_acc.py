import requests
import pandas as pd
from datetime import datetime,timedelta

from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.models import Variable  

def current_time():
    return datetime.now().strftime("%Y%m%d")

def fetch_data():
    category_name = "남성액세서리"

    category_list = ['271101100','271102100','271115100','271112100','271109100','271106100'
                '271104100','271105100','271103100','271116100','271119100','271117100','271113100',
                '271108100','271118100']

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5042.108 Safari/537.36",
    }

    # 데이터프레임에 저장할 리스트 초기화
    items_list = []

    crawling_time = current_time()

    for category in category_list:
        # API URL (네트워크 탭에서 확인한 URL)
        url = f'https://recommend-api.29cm.co.kr/api/v4/best/items?categoryList={category}&periodSort=ONE_DAY&limit=100&offset=0'

        # 요청 보내기
        response = requests.get(url, headers=headers)

        data = response.json()

        if data['result'] == "SUCCESS" : 
            items = data['data']['content']

            for rank, item in enumerate(items[:10], start=1):
                # 필요한 정보 추출
                item_info = {
                    'product_name': item['itemName'],  # 아이템 이름
                    'image_link': f'https://img.29cm.co.kr/{item["imageUrl"]}',  # 이미지 URL
                    'product_link': f"https://product.29cm.co.kr/catalog/{item['itemNo']}?category_large_code={item['frontCategoryInfo'][0]['category1Code']}", # 상품링크
                    'rank': rank, # 상품 순위
                    'date': crawling_time, # 해당 상품 수집 시 시간(년도월일)
                    'data_creation_time':crawling_time, # 해당 상품 수집 시 시간(년도월일)
                    'category': f"{item['frontCategoryInfo'][0]['category1Name']}_{item['frontCategoryInfo'][0]['category2Name']}" if item['frontCategoryInfo'][0]['category2Name'] == "EXCLUSIVE" or item['frontCategoryInfo'][0]['category2Name'] == '해외브랜드' else item['frontCategoryInfo'][0]['category2Name'], # 상품 카테고리
                    'price': item['lastSalePrice'],  # 마지막 판매 가격
                    # 'gender': item['frontCategoryInfo'][0]['category1Name'][:2], # 동일한 아이템의 성별이 남,녀 모두 있는 경우에 아이템의 랭킹이 다른문제가 있음.
                    'gender': 'men' if category_name[:2] == "남성" else 'women' # 성별 
                }
                items_list.append(item_info)  # 리스트에 추가
        else : 
            pass
        

    # DataFrame 생성 후 CSV로 저장
    df = pd.DataFrame(items_list)
    df['date'] = pd.to_datetime(df['date'], errors='coerce').dt.strftime('%Y-%m-%d')
    df['data_creation_time'] = pd.to_datetime(df['data_creation_time'], errors='coerce').dt.strftime('%Y-%m-%d')
    df.to_csv(f'/opt/airflow/data/29cm_{category_name}_{crawling_time}.csv', mode='w', index=False, header=True)

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 7, 25),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    '29cm_male_acc_dag',
    default_args=default_args,
    description='Collect male accessories data of 29cm',
    schedule_interval='10 10 * * *', # 매일 저녁 19시 10분 ( utc 기준 실행 )
    catchup = False
)

fetch_task = PythonOperator(
    task_id='29cm_male_acc_gathering',
    python_callable=fetch_data,
    dag=dag,
)