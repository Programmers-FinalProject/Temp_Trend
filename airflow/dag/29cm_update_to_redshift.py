from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import pandas as pd
import boto3
from sqlalchemy import create_engine
from airflow.hooks.base_hook import BaseHook

# S3에서 CSV 파일을 읽고 Redshift에 업로드하는 함수
def merge_and_upload_to_redshift():
    # S3에서 CSV 파일 읽기
    BUCKET_NAME = BaseHook.get_connection('MyS3Conn').extra_dejson.get('bucket_name')
    s3_client = boto3.client('s3')

    # S3에서 모든 CSV 파일 목록 가져오기
    prefix = 'crawling/'
    response = s3_client.list_objects_v2(Bucket=BUCKET_NAME, Prefix=prefix)

    df_list = []
    today_str = datetime.now().strftime("%Y%m%d")
    
    if 'Contents' in response:
        for obj in response['Contents']:
            file_key = obj['Key']
            if file_key.endswith('.csv') and today_str in file_key :
                # S3에서 CSV 파일 읽기
                csv_file = s3_client.get_object(Bucket=BUCKET_NAME, Key=file_key)
                df = pd.read_csv(csv_file['Body'])
                df_list.append(df)

    # 모든 데이터프레임을 하나로 통합
    if df_list:
        merged_df = pd.concat(df_list, ignore_index=True)

        # Redshift에 연결
        redshift_conn = BaseHook.get_connection('Redshift_cluster_hori1')
        engine = create_engine(f'redshift+psycopg2://{redshift_conn.user}:{redshift_conn.password}@{redshift_conn.host}:{redshift_conn.port}/{redshift_conn.database}')

        # 데이터프레임을 Redshift에 업로드
        merged_df.to_sql('shop_29cm', engine, schema='raw_data', index=False, if_exists='append')  # 'append'로 설정하여 기존 데이터에 추가

        print("데이터가 Redshift에 업로드되었습니다.")
    else:
        print("업로드할 데이터가 없습니다.")

# DAG 설정
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    '29cm_s3_to_redshift',
    default_args=default_args,
    description='Fetch today\'s data from S3 and upload to Redshift',
    schedule_interval='30 23 * * *',  # 매일 저녁 11시 30분
    start_date=datetime(2024, 8, 1),  
    catchup=False,
)

# 태스크 정의
upload_task = PythonOperator(
    task_id='merge_and_upload_to_redshift',
    python_callable=merge_and_upload_to_redshift,
    dag=dag,
    queue='queue1'
)

upload_task