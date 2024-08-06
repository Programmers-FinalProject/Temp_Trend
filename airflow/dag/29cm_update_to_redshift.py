import logging
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import pandas as pd
import boto3
from io import BytesIO

from airflow.hooks.base_hook import BaseHook
from airflow.hooks.S3_hook import S3Hook
from airflow.providers.amazon.aws.transfers.s3_to_redshift import S3ToRedshiftOperator
from airflow.providers.amazon.aws.operators.s3 import S3ListOperator
from airflow.models import Variable
from botocore.exceptions import NoCredentialsError


# 파일 읽고 병합 및 임시 파일 삭제
def merge_files(**kwargs):
    logger = logging.getLogger(__name__)
    s3_client = boto3.client('s3',
                            aws_access_key_id=Variable.get('ACCESS_KEY'),
                            aws_secret_access_key=Variable.get('SECRET_KEY')
                            )
    bucket_name = Variable.get('s3_bucket')
    today_str = datetime.now().strftime('%Y%m%d')
    file_keys = kwargs['task_instance'].xcom_pull(task_ids='list_s3_files')

    combined_df = pd.DataFrame()
    files_to_delete = []

    # for key in file_keys:
    #     logger.info(f'Files : {key}')
    #     if today_str in key and 'bestitem' not in key:
    #         logger.info(f'Combine Target Files : {key}')
    #         response = s3_client.get_object(Bucket=bucket_name, Key=key)
    #         df = pd.read_csv(BytesIO(response['Body'].read()))
    #         logger.info(f'Data Frame Header Top3 : {df.head(3)}')
    #         combined_df = pd.concat([combined_df, df], ignore_index=True)
    #         files_to_delete.append(key)  # 삭제할 파일 목록에 키 추가

    # combined_df['price'] = combined_df['price'].replace(',', '', regex=True).astype(float)
    # combined_df['category3'] = combined_df['category3'].fillna('')  # NaN을 NULL로 변환


    # # 합쳐진 데이터프레임을 CSV로 저장하거나 다른 작업 수행
    # file_name = f"29cm_bestitem_{today_str}.csv"
    # local_file_path = f"/opt/airflow/data/{file_name}"

    # combined_df.to_csv(local_file_path, index=False)
    # s3_client.upload_file(local_file_path, bucket_name, f'crawling/{file_name}')
    # logger.info(f'Upload Files : {file_name}')

    # # 읽어온 파일들을 S3에서 삭제
    # if files_to_delete:
    #     delete_response = s3_client.delete_objects(
    #         Bucket=bucket_name,
    #         Delete={
    #             'Objects': [{'Key': key} for key in files_to_delete],
    #             'Quiet': True  # 삭제 결과를 반환하지 않으려면 True로 설정
    #         }
    #     )
    #     logger.info(f"Deleted files: {delete_response.get('Deleted', [])}")  # 삭제된 파일 목록 출력

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

# S3에서 파일 목록 가져오기
list_s3_files = S3ListOperator(
    task_id='list_s3_files',
    bucket=Variable.get('s3_bucket'),
    prefix='crawling',
    delimiter=',',
    aws_conn_id='MyS3Conn',
    dag=dag,
    queue='queue1'
)

# 파일 병합 작업 정의
merge_s3_files = PythonOperator(
    task_id='merge_s3_files',
    python_callable=merge_files,
    provide_context=True,
    dag=dag,
    queue='queue1'
)

today_str = datetime.now().strftime('%Y%m%d')
s3_to_redshift_task = S3ToRedshiftOperator(
    task_id='s3_to_redshift_task',
    schema='raw_data',  # Redshift의 스키마
    table='shop_29cm',  # Redshift의 테이블명
    s3_bucket=Variable.get("s3_bucket"),
    # s3_key=f'crawling/29cm_bestitem_{today_str}.csv',  # Airflow의 템플릿 변수를 사용하여 오늘 날짜를 포함
    s3_key='crawling/29cm_bestitem_20240805.csv',  # Airflow의 템플릿 변수를 사용하여 오늘 날짜를 포함
    copy_options=['CSV',"IGNOREHEADER 1"],
    aws_conn_id='MyS3Conn',  # Redshift 연결 ID
    redshift_conn_id='Redshift_cluster_hori1',  # Redshift 연결 ID
    method="APPEND",
    dag=dag,
    queue='queue1'
)

list_s3_files >> merge_s3_files >> s3_to_redshift_task
