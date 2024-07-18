from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.models import Variable
from datetime import datetime, timedelta
from common import weatherF

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
    stnData = weatherF.weatherApiParser2(weatherF.weatherApi(Variable.get("stnDomain"), stnOption), columns=Variable.get("stnColumns"))
    weatherF.weatherCSVmaker("data/", f"stnDataCsv",stnData)
    print("STNDATA :  " , stnData)

# PythonOperator를 사용하여 작업 정의
stnApiTask = PythonOperator(
    task_id='stnApiTask',
    python_callable=stnApi,
    dag=dag,
)

# DAG 설정
stnApiTask


