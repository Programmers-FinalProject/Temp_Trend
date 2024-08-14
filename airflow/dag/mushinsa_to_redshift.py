from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.models import Variable
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.providers.amazon.aws.transfers.s3_to_redshift import S3ToRedshiftOperator
from airflow.utils.dates import days_ago
from datetime import datetime

# 기본 인수 설정
default_args = {
    'owner': 'airflow',
    'start_date': datetime(2024, 1, 1),
    'catchup' : False,
    'retries': 1,
}

# DAG 정의
dag = DAG(
    dag_id = 'mushinsa_to_redshift',
    default_args=default_args,
    schedule_interval='00 20 * * *',
    max_active_runs=1,
)

# S3 버킷과 파일 정보
S3_BUCKET = 'team-hori-1-bucket'
S3_KEY = 'musinsa.csv'
REDSHIFT_TABLE = 'musinsa'
REDSHIFT_SCHEMA = 'musinsa'
AWS_ACCESS_KEY_ID = Variable.get('ACCESS_KEY')
AWS_SECRET_ACCESS_KEY = Variable.get('SECRET_KEY')

# Redshift 연결 ID
REDSHIFT_CONN_ID = 'Redshift_cluster_hori1'

# 테이블 드랍 및 생성 쿼리
drop_table_sql = f"""
    DROP TABLE IF EXISTS {REDSHIFT_SCHEMA}.{REDSHIFT_TABLE};
"""

# 테이블 생성 쿼리
create_table_sql = f"""
    CREATE TABLE {REDSHIFT_SCHEMA}.{REDSHIFT_TABLE} (
        "product_name" TEXT,
        "product_link" TEXT,
        "image_link" TEXT,
        "rank" INTEGER,
        "date" TIMESTAMP,
        "data_creation_time" TIMESTAMP,
        "category" TEXT,
        "price" INTEGER,
        "gender" TEXT 
    );
"""

# 테이블 드랍 작업 정의
drop_table = PostgresOperator(
    task_id='drop_table',
    postgres_conn_id=REDSHIFT_CONN_ID,
    sql=drop_table_sql,
    dag=dag,
    queue='queue1',
)

# 테이블 생성 작업 정의
create_table = PostgresOperator(
    task_id='create_table',
    postgres_conn_id=REDSHIFT_CONN_ID,
    sql=create_table_sql,
    dag=dag,
    queue='queue1',
)

# S3에서 Redshift로 데이터를 로드하는 작업 정의
load_to_redshift = S3ToRedshiftOperator(
    task_id='load_csv_from_s3_to_redshift',
    schema=REDSHIFT_SCHEMA,
    table=REDSHIFT_TABLE,
    s3_bucket=S3_BUCKET,
    s3_key=S3_KEY,
    copy_options=["CSV", "IGNOREHEADER 1", "DELIMITER ','"],
    aws_conn_id='MyS3Conn',  # AWS 연결 ID, Airflow에서 설정한 ID
    redshift_conn_id=REDSHIFT_CONN_ID,
    dag=dag,
    queue='queue1',
)

# 작업 순서 정의
drop_table>> create_table >> load_to_redshift
