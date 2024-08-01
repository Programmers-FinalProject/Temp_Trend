from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

# 기본 DAG 인자 설정
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# DAG 정의
dag = DAG(
    'test_dag_이름바꾼거_적용되는지_확인',
    default_args=default_args,
    description='A simple test DAG',
    schedule_interval=timedelta(days=1),
    start_date=datetime(2023, 7, 16),
    catchup=False,
)

# 작업 함수 정의
def print_hello():
    print("Hello World!")

# PythonOperator를 사용하여 작업 정의
hello_task = PythonOperator(
    task_id='hello_task',
    python_callable=print_hello,
    dag=dag,
)

# DAG 설정
hello_task
