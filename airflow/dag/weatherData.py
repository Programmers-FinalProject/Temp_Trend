from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.models import Variable
from datetime import datetime, timedelta
from dag.utils import weatherF
# 오늘 날짜 
now = datetime.now()
today = now.strftime('%Y%m%d')
today = today
# 기본 DAG 인자 설정
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

weApiOption = {
    "serviceKey" : Variable.get("weatherServiceKey"),
    "pageNo" : '1',
    "numOfRows" : Variable.get("numOfRows"),
    "dataType" : 'JSON',
    "base_date" : today,
    "base_time" : "0500",
}
# DAG 정의
dag = DAG(
    'WeatherDag',
    default_args=default_args,
    description='전국 기상 데이터 API호출',
    schedule_interval=timedelta(days=1),
    start_date=datetime(2023, 7, 19),
    catchup=False,
)

# 작업 함수 정의
def weatherX33Y126():
    weApiOption["nx"] = "33"
    weApiOption["ny"] = "126"
    apidata = weatherF.weatherApiJSONParser(weatherF.weatherApi(Variable.get("weDomain"), weApiOption))
    weatherF.weatherCSVmaker("", f"weatherAPIData_{weApiOption['nx']},{weApiOption['ny']}",apidata)
    print(f"APIDATA {weApiOption['nx']},{weApiOption['ny']} : " , apidata)

# PythonOperator를 사용하여 작업 정의
weatherX33Y126Task = PythonOperator(
    task_id='weatherX33Y126Task',
    python_callable=weatherX33Y126,
    dag=dag,
)

# DAG 설정
weatherX33Y126Task

