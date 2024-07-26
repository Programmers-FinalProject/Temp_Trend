from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.models import Variable
from datetime import datetime, timedelta
from utils import weatherF
import boto3, json

s3_client = boto3.client(
    's3',
    aws_access_key_id =  Variable.get("ACCESS_KEY"),
    aws_secret_access_key = Variable.get("SECRET_KEY"),
)

# 기본 DAG 인자 설정
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}
stnOption = {
    "inf":"SFC",
    "authKey" : Variable.get("weatherAuth"),
}

# DAG 정의
dag = DAG(
    'weatherStation',
    default_args=default_args,
    description='예보 지역 데이터 API호출',
    schedule_interval=timedelta(days=1),
    start_date=datetime(2023, 7, 19),
    catchup=False,
)

# 작업 함수 정의
def stnApi():
    s3_bucket = Variable.get("s3_bucket")
    s3_csv_path = Variable.get("we_s3_csv_path")
    
    stnData = weatherF.weatherApiParser2(weatherF.weatherApi(Variable.get("stnDomain"), stnOption), columns=json.loads(Variable.get("stnColumns")))
    weatherF.weatherCSVmaker(s3_bucket, f"{s3_csv_path}stnDataCsv.csv",stnData,s3_client)
    
    print("STNDATA :  " , stnData)

# PythonOperator를 사용하여 작업 정의
stnApiTask = PythonOperator(
    task_id='stnApiTask',
    python_callable=stnApi,
    dag=dag,
)

# DAG 설정
stnApiTask


