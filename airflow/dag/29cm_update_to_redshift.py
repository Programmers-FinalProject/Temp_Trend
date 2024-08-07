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
from airflow.sensors.external_task_sensor import ExternalTaskSensor
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

    for key in file_keys:
        logger.info(f'Files : {key}')
        if today_str in key and 'bestitem' not in key:
            logger.info(f'Combine Target Files : {key}')
            response = s3_client.get_object(Bucket=bucket_name, Key=key)
            df = pd.read_csv(BytesIO(response['Body'].read()))
            logger.info(f'Data Frame Header Top3 : {df.head(3)}')
            combined_df = pd.concat([combined_df, df], ignore_index=True)
            files_to_delete.append(key)  # 삭제할 파일 목록에 키 추가

    combined_df['price'] = combined_df['price'].replace(',', '', regex=True).astype(float)
    combined_df['category3'] = combined_df['category3'].fillna('')  # NaN을 NULL로 변환


    # 합쳐진 데이터프레임을 CSV로 저장하거나 다른 작업 수행
    file_name = f"29cm_bestitem_{today_str}.csv"
    local_file_path = f"/opt/airflow/data/{file_name}"

    combined_df.to_csv(local_file_path, index=False)
    s3_client.upload_file(local_file_path, bucket_name, f'crawling/{file_name}')
    logger.info(f'Upload Files : {file_name}')

    # XCom에 삭제할 파일 목록 저장
    kwargs['task_instance'].xcom_push(key='files_to_delete', value=files_to_delete)
    kwargs['task_instance'].xcom_push(key='uploaded_file', value=f'crawling/{file_name}')

def delete_files(**kwargs):
    logger = logging.getLogger(__name__)
    s3_client = boto3.client('s3',
                            aws_access_key_id=Variable.get('ACCESS_KEY'),
                            aws_secret_access_key=Variable.get('SECRET_KEY')
                            )
    bucket_name = Variable.get('s3_bucket')
    files_to_delete = kwargs['task_instance'].xcom_pull(key='files_to_delete', task_ids='merge_files')
    
    if files_to_delete:
        delete_response = s3_client.delete_objects(
            Bucket=bucket_name,
            Delete={
                'Objects': [{'Key': key} for key in files_to_delete],
                'Quiet': True
            }
        )
        logger.info(f"Deleted files: {delete_response.get('Deleted', [])}")

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
    schedule_interval='20 14 * * *',  # 매일 저녁 11시 20분
    start_date=datetime(2024, 8, 1),  
    catchup=False,
)

today_str = datetime.now().strftime('%Y%m%d')

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

# 외부 DAG의 태스크가 완료될 때까지 기다리는 External Task Sensor 추가
external_dag_ids = [
    '29cm_female_acc_data_extract',
    '29cm_female_bag_data_extract',
    '29cm_female_shoes_data_extract',
    '29cm_female_clothes_data_extract',
    '29cm_male_acc_data_extract',
    '29cm_male_bag_data_extract',
    '29cm_male_shoes_data_extract',
    '29cm_male_clothes_data_extract',
]

wait_for_external_dags = []

for dag_id in external_dag_ids:
    sensor = ExternalTaskSensor(
        task_id=f'wait_for_{dag_id}',
        external_dag_id=dag_id,
        external_task_id='fetch_product_links',  # 각 DAG의 완료를 확인할 태스크 ID
        execution_date_fn=lambda execution_date: execution_date,  # 현재 DAG의 execution_date 사용
        mode='all_success',
        timeout=600,
        dag=dag,
    )
    wait_for_external_dags.append(sensor)


# 파일 병합 작업 정의
merge_s3_files = PythonOperator(
    task_id='merge_s3_files',
    python_callable=merge_files,
    provide_context=True,
    dag=dag,
    queue='queue1'
)

delete_files_task = PythonOperator(
        task_id='delete_files',
        python_callable=delete_files,
        provide_context=True,
        dag=dag,
        queue='queue1'
)

s3_to_redshift_task = S3ToRedshiftOperator(
    task_id='s3_to_redshift_task',
    schema='raw_data',  # Redshift의 스키마
    table='shop_29cm',  # Redshift의 테이블명
    s3_bucket=Variable.get("s3_bucket"),
    s3_key=f'crawling/29cm_bestitem_{today_str}.csv',  # Airflow의 템플릿 변수를 사용하여 오늘 날짜를 포함
    copy_options=['CSV',"IGNOREHEADER 1"],
    aws_conn_id='MyS3Conn',  # Redshift 연결 ID
    redshift_conn_id='Redshift_cluster_hori1',  # Redshift 연결 ID
    method="APPEND",
    dag=dag,
    queue='queue1'
)

# 태스크 종속성 설정
list_s3_files >> wait_for_external_dags[0]  # 첫 번째 ExternalTaskSensor와 연결
for sensor in wait_for_external_dags[1:]:
    wait_for_external_dags[0] >> sensor  # 첫 번째 센서를 나머지 센서와 연결

wait_for_external_dags[-1] >> merge_s3_files >> s3_to_redshift_task >> delete_files_task
