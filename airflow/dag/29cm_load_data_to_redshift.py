from airflow import DAG
from airflow.providers.amazon.aws.transfers.s3_to_redshift import S3ToRedshiftOperator
from datetime import datetime, timedelta
from airflow.models import Variable

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
    's3_to_redshift_dag',
    default_args=default_args,
    description='Load data from S3 to Redshift',
    schedule_interval='30 23 * * *',  # 매일 23시 30분에 실행
)

# S3에서 Redshift로 데이터 로드 작업
load_data_task = S3ToRedshiftOperator(
    task_id='load_data_to_redshift',
    schema='webcrawling',  # Redshift 스키마
    table='bestitems_29cm',  # Redshift 테이블 이름
    s3_bucket=Variable.get("S3_BUCKET_NAME"),  # S3 버킷 이름
    s3_key='crawling/29cm_{{ ds_nodash }}_best_items.csv',  # S3 파일 경로
    copy_options=['CSV', 'IGNOREHEADER 1'],  # COPY 옵션
    aws_conn_id='MyS3Conn',  # Airflow에 설정된 AWS 연결 ID
    redshift_conn_id='redshift_default',  # Airflow에 설정된 Redshift 연결 ID
    dag=dag,
)

# 태스크 설정
load_data_task