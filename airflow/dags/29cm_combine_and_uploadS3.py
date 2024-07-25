import os
import pandas as pd
import boto3

from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.models import Variable

def combine_csv_files(**kwargs):
    # 당일 날짜를 가져옴
    today_date = datetime.now().strftime("%Y%m%d")
    
    # 파일 경로 설정
    data_directory = '/opt/airflow/data/'
    combined_file_path = os.path.join(data_directory, f'29cm_{today_date}_best_items.csv')
    
    # CSV 파일 목록 수집
    csv_files = [
        os.path.join(data_directory, f'29cm_{category}_{today_date}.csv')
        for category in ['남성가방', '남성신발', '남성액세서리', '남성의류', '여성가방', '여성신발', '여성액세서리', '여성의류']  # 카테고리 이름 리스트
    ]

    # CSV 파일 병합
    combined_data = []
    for file in csv_files:
        if os.path.exists(file):
            with open(file, 'r', encoding='utf-8') as f:
                # 파일 내용을 읽고 combined_data에 추가
                combined_data.extend(f.readlines()[1:])  # 첫 번째 줄(헤더 제외)
    
    # 병합된 데이터를 파일로 저장
    with open(combined_file_path, 'w', encoding='utf-8') as f:
        # 파일의 첫 번째 줄(헤더) 추가
        f.write('product_name,image_link,product_link,rank,date,data_creation_time,category,price,gender\n')
        f.writelines(combined_data)
    
    return combined_file_path

def upload_to_s3():
    
    today_date = datetime.now().strftime("%Y%m%d")
    S3_BUCKET_NAME = Variable.get("S3_BUCKET_NAME")  
    AWS_ACCESS_KEY_ID = Variable.get("ACCESS_KEY")  
    AWS_SECRET_ACCESS_KEY = Variable.get("SECRET_KEY")  

    s3_file_name = f'crawling/29cm_{today_date}_best_items.csv'

    
    data_directory = '/opt/airflow/data/'
    file_path = os.path.join(data_directory, f'29cm_{today_date}_best_items.csv')

    s3 = boto3.client(
                    's3',
                    aws_access_key_id=AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                    region_name="ap-northeast-2")
    
    s3.upload_file(file_path, S3_BUCKET_NAME, s3_file_name)

# 기본 인자 설정
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 7, 25),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    'catchup': False,
}

# DAG 정의
dag = DAG(
    'combine_and_upload_to_s3',
    default_args=default_args,
    description='Combine daily CSV files and upload to S3',
    schedule_interval='20 23 * * *',  # 매일 23시에 실행
)


# CSV 파일 병합 작업
combine_task = PythonOperator(
    task_id='29cm_combine_csv_files',
    python_callable=combine_csv_files,
    provide_context=True,
    dag=dag,
)

# S3 업로드 작업
upload_task = PythonOperator(
    task_id='upload_to_s3',
    python_callable=upload_to_s3,
    dag=dag,
)

# 태스크 순서 설정
combine_task >> upload_task