from datetime import datetime
import pandas as pd
import os
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.models import Variable
import boto3

# S3 업로드 함수
def upload_to_s3(bucket_name, file_name):
    etl_time = datetime.now().strftime("%Y%m%d")
    AWS_ACCESS_KEY_ID = Variable.get('ACCESS_KEY')
    AWS_SECRET_ACCESS_KEY = Variable.get('SECRET_KEY')
    s3_client = boto3.client('s3',
                             aws_access_key_id=AWS_ACCESS_KEY_ID,
                             aws_secret_access_key=AWS_SECRET_ACCESS_KEY
                             )
    s3_client.upload_file(file_name, bucket_name, f'crawling/29cm_merged_data_{etl_time}.csv')
    print(f"{file_name}를 {bucket_name}에 업로드했습니다.")

# 데이터 병합 및 저장 함수
def merge_data_and_upload():
    etl_time = datetime.now().strftime("%Y%m%d")
    data_dir = '/opt/airflow/data/'
    output_file = os.path.join(data_dir, f'29cm_merged_data_{etl_time}.csv')

    # 데이터 프레임 리스트
    df_list = []

    # 각 카테고리의 파일을 읽어와서 리스트에 추가
    categories = [
        f'29cm_여성액세서리_{etl_time}',
        f'29cm_여성가방_{etl_time}',
        f'29cm_여성의류_{etl_time}',
        f'29cm_여성신발_{etl_time}',
        f'29cm_남성악세서리_{etl_time}',
        f'29cm_남성가방_{etl_time}',
        f'29cm_남성의류_{etl_time}',
        f'29cm_남성신발_{etl_time}',
    ]

    for category in categories:
        file_path = os.path.join(data_dir, f'{category}.csv')
        if os.path.exists(file_path):
            df = pd.read_csv(file_path)
            df_list.append(df)

    # 데이터 프레임 병합
    if df_list:
        merged_df = pd.concat(df_list, ignore_index=True)
        merged_df.to_csv(output_file, index=False, encoding='utf-8-sig')
        print("데이터 병합 완료 및 저장됨:", output_file)

        # S3 업로드
        upload_to_s3(Variable.get('s3_bucket'), output_file)
    else:
        print("병합할 데이터가 없습니다.")

# DAG 정의
default_args = {
    'owner': 'airflow',
    'start_date': datetime(2024, 8, 1),
    'retries': 0,
}

dag = DAG(
    '29cm_data_merge_and_upload',
    default_args=default_args,
    description='Merge data from multiple DAGs and upload to S3',
    schedule_interval='20 14 * * *',  # 매일 UTC 14시 20분에 실행 (한국시간 23시 20분)
)

# 태스크 정의
merge_task = PythonOperator(
    task_id='merge_and_upload_data',
    python_callable=merge_data_and_upload,
    dag=dag,
)
