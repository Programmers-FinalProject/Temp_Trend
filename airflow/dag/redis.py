from airflow.decorators import task
from airflow.models import Variable
from airflow.utils.dates import days_ago
import requests
import pandas as pd
from io import StringIO
import re
import urllib.parse
import html
from bs4 import BeautifulSoup
from datetime import datetime
import pytz
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from airflow.providers.amazon.aws.hooks.redshift_sql import RedshiftSQLHook
from airflow.providers.amazon.aws.transfers.s3_to_redshift import S3ToRedshiftOperator
from airflow import DAG

def decode_html_entities(text):
    return html.unescape(text)

def remove_html_tags(text):
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)

def get_image_from_url(news_url):
    try:
        html_content = requests.get(news_url).text
        soup = BeautifulSoup(html_content, "html.parser")
        meta_og_image = soup.find("meta", property="og:image")
        if meta_og_image:
            return meta_og_image["content"]
        else:
            return "not found -> meta tag og:image"
    except Exception as e:
        print(f"get_meta_og_image | error: {e}")
        return None

# 기본 인자 설정
default_args = {
    'owner': 'airflow',
    'start_date': days_ago(1),
    'retries': 0,
}

with DAG(
    dag_id='news_S3_REDSHIFT',
    default_args=default_args,
    schedule_interval='0 * * * *',
    catchup=False,
) as dag :
    
    @task(queue='queue1')
    def fetch_and_store_news():
        # Airflow 환경변수에서 값 가져오기
        client_id = Variable.get("naver-client-id")
        client_secret = Variable.get("naver-client-secret")

        if not client_id or not client_secret:
            raise ValueError("Client ID or Client Secret not found in Airflow variables")
    
        encText = urllib.parse.quote("날씨")
        sorting = "&display=100&start=1&sort=sim"
        url = "https://openapi.naver.com/v1/search/news?query=" + encText + sorting

        headers = {
            'X-Naver-Client-Id': client_id,
            'X-Naver-Client-Secret': client_secret,
        }

        response = requests.get(url, headers=headers)
    
        if response.status_code == 200:
            data = response.json()
            items = data['items']
            plus_data = []
            for idx, item in enumerate(items):
                # 키를 고유 ID로 설정. 1부터 시작
                item_id = f"news:{idx+1}"
                clean_title = decode_html_entities(remove_html_tags(item['title']))
                clean_description = decode_html_entities(remove_html_tags(item['description']))
                image_url = get_image_from_url(item['link'])
                
                context = {
                    "id" : item_id,
                    "title": clean_title,
                    "description": clean_description,
                    "link": item['link'],
                    "pubDate": item['pubDate'],
                    "image_url": image_url if image_url else ""
                }
                plus_data.append(context)
        
            df = pd.DataFrame(plus_data)
            return df
        else:
            raise ValueError("Failed to fetch news data from API")
    @task(queue='queue1')
    def create_redshift_table():
        redshift_hook = RedshiftSQLHook(redshift_conn_id='my_redshift_conn')
        create_table_query = """
        CREATE TABLE IF NOT EXISTS raw_data.news_weather_table (
            title VARCHAR(65535),
            description VARCHAR(65535),
            link VARCHAR(2048),
            pubDate VARCHAR(2048),
            image_url VARCHAR(2048)
        );
        """
        redshift_hook.run(create_table_query)
        print("Redshift table created successfully.")

    @task(queue='queue1')
    def s3_upload(df):
        if df is not None and not df.empty:
            csv_buffer = StringIO()
            df.to_csv(csv_buffer, index=False)

            aws_hook = S3Hook(aws_conn_id='my_amazon_conn')
            bucket_name = "team-hori-1-bucket"
            
            korea_timezone = pytz.timezone("Asia/Seoul")
            current_time = datetime.now(korea_timezone)
            formatted_time = current_time.strftime("%Y%m%d")
            
            s3_key = f'news/news_{formatted_time}.csv'
            
            aws_hook.load_string(
                string_data=csv_buffer.getvalue(),
                key=s3_key,
                bucket_name=bucket_name,
                replace=True
            )

            print(f"Dataframe uploaded to S3 successfully: {s3_key}")
            return s3_key
        else:
            raise ValueError("Dataframe is empty or None")

    create_table = create_redshift_table()
    news_df = fetch_and_store_news()
    s3_key = s3_upload(news_df)
    
    s3_to_redshift = S3ToRedshiftOperator(
        task_id="s3_to_redshift",
        s3_bucket="team-hori-1-bucket",
        s3_key=s3_key
        schema="raw_data",
        table="news_weather_table",
        copy_options=['csv', 'IGNOREHEADER 1'],
        aws_conn_id="my_amazon_conn",
        redshift_conn_id="my_redshift_conn",
        queue='queue1',
        dag = dag
    )
    create_table >> news_df >> s3_key >> s3_to_redshift