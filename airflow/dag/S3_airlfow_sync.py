from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 7, 24),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    's3_sync_dag',
    default_args=default_args,
    description='Sync S3 bucket with local directory',
    schedule_interval=timedelta(minutes=10),
)

sync_task = BashOperator(
    task_id='sync_s3_to_local',
    bash_command='aws s3 sync s3://team-hori-dags /opt/airflow/dags --delete',
    dag=dag,
)
