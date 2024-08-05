import logging
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import pandas as pd
import boto3
from sqlalchemy import create_engine
from airflow.hooks.base_hook import BaseHook
from airflow.hooks.S3_hook import S3Hook
from airflow.providers.amazon.aws.transfers.s3_to_redshift import S3ToRedshiftOperator
from airflow.models import Variable
from botocore.exceptions import NoCredentialsError

# S3에서 CSV 파일을 읽어 하나로 합치는 함수 읽은 파일은 삭제
def merge_and_upload_to_s3():
    logger = logging.getLogger(__name__)
    # S3에서 CSV 파일 읽기
    s3_connection = S3Hook('MyS3Conn')
    BUCKET_NAME = s3_connection.get_bucket(Variable.get("s3_bucket")) # s3.Bucket(name='team-hori-1-bucket')
    logger.info(f'Bucket Check ....... : {BUCKET_NAME}')
    # BUCKET_NAME = BaseHook.get_connection('MyS3Conn').extra_dejson.get('bucket_name')

    # S3에서 모든 CSV 파일 목록 가져오기
    prefix = 'crawling/'
    
    today_str = datetime.now().strftime("%Y%m%d")
    try:
        # S3에서 객체 목록 가져오기
        keys = s3_connection.list_keys(bucket_name = BUCKET_NAME, prefix=prefix)
        logger.info(f'File in Directory Check ....... : {keys}')
        if not keys :
            logger.info('No files found in the S3 bucket')
            return
        
        csv_files=[]
        for file in keys :
            filepath = f's3://{Variable.get("s3_bucket")}/{file}'
            logger.info(f'File list .......... : {filepath}')
            if filepath in today_str :
                csv_files.append(filepath)
                
        # CSV 파일 목록 수집
        # csv_files = [key for key in keys if key.endswith('.csv') and today_str in key]
        # logger.info(f'Read File 29cm {today_str} file List ........ : {csv_files}')
        # CSV 파일 병합 로직
        if not csv_files:
            print("No CSV files found for today's date.")
            return
        
        combined_df = pd.DataFrame()
        
        for csv_file in csv_files:
            # S3에서 CSV 파일 읽기
            s3_object = s3_connection.get_key(csv_file, BUCKET_NAME)
            df = pd.read_csv(s3_object.get()['Body'])
            combined_df = pd.concat([combined_df, df], ignore_index=True)

            s3_connection.delete_objects(bucket_name=BUCKET_NAME, keys=[csv_file])
        
        # S3에 합쳐진 DataFrame 저장
        output_key = f'crawling/29cm_bestitem_{today_str}.csv'
        combined_df.to_csv(f'/opt/airflow/data/29cm_bestitem_{today_str}.csv', index=False)  # 로컬 파일로 저장
        s3_connection.load_file(f'/opt/airflow/data/29cm_bestitem_{today_str}.csv', output_key, bucket_name=BUCKET_NAME, replace=True)  # S3로 업로드

        
        logger.info(f"Combined file uploaded to S3: {output_key}")

    except Exception as e:
        logger.info(f"An error occurred: {e}")

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
    schedule_interval='30 14 * * *',  # 매일 저녁 11시 30분
    start_date=datetime(2024, 8, 1),  
    catchup=False,
)

merge_and_upload_task = PythonOperator(
    task_id='merge_and_upload_task',
    python_callable=merge_and_upload_to_s3,
    dag=dag,
    queue='queue1'
)

s3_to_redshift_task = S3ToRedshiftOperator(
    task_id='s3_to_redshift_task',
    schema='raw_data',  # Redshift의 스키마
    table='shop_29cm',  # Redshift의 테이블명
    s3_bucket=Variable.get("s3_bucket"),
    s3_key=f'crawling/29cm_bestitem_{{ ds_nodash }}.csv',  # Airflow의 템플릿 변수를 사용하여 오늘 날짜를 포함
    copy_options=['CSV'],
    aws_conn_id='MyS3Conn',  # Redshift 연결 ID
    redshift_conn_id='Redshift_cluster_hori1',  # Redshift 연결 ID
    method="APPEND",
    dag=dag,
    queue='queue1'
)

merge_and_upload_task >> s3_to_redshift_task