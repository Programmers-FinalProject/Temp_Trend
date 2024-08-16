from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.task_group import TaskGroup
from airflow.models import Variable
from datetime import datetime, timedelta
from utils import weatherF, redShiftUtils
import boto3, json, psycopg2

s3_client = boto3.client(
    's3',
    aws_access_key_id =  Variable.get("ACCESS_KEY"),
    aws_secret_access_key = Variable.get("SECRET_KEY"),
)
s3_bucket = Variable.get("s3_bucket")
s3_csv_path = Variable.get("we_s3_csv_path")
# 기본 DAG 인자 설정
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}
weather_code_JSON = {
  "POP": "강수확률 (%)",
  "PTY": "강수형태 (코드값)",
  "PCP": "1시간 강수량 (범주 1 mm)",
  "REH": "습도 (%)",
  "SNO": "1시간 신적설 (범주 1 cm)",
  "SKY": "하늘상태 (코드값)",
  "TMP": "1시간 기온 (℃)",
  "TMN": "일 최저기온 (℃)",
  "TMX": "일 최고기온 (℃)",
  "UUU": "풍속(동서성분) (m/s)",
  "VVV": "풍속(남북성분) (m/s)",
  "WAV": "파고 (M)",
  "VEC": "풍향 (deg)",
  "WSD": "풍속 (m/s)"
}
stnOption = {
    "inf":"SFC",
    "authKey" : Variable.get("weatherAuth"),
}

# DAG 정의
dag = DAG(
    'weatherSetting',
    default_args=default_args,
    description='예보 지역 데이터 API호출',
    start_date=datetime(2024, 7, 26),
    catchup=False,
    schedule_interval=None,
)

def weatherCodeTable():
    weatherF.weather_code_create()

    sql = "INSERT INTO raw_data.weather_code (weather_code, weather_code_desc) VALUES "
    values = []
    for code, desc in weather_code_JSON.items():
        values.append(f"('{code}', '{desc}')")
    sql += ",".join(values) + ";"
    sql = [sql]
    redShiftUtils.sql_execute_to_redshift(sql)

def weatherDataTable():
    weatherF.weather_data_create()

def weatherStnTable():
    weatherF.weather_stn_create()

def weatherStnDataToRedshift():
    s3CsvData = weatherF.CSVdownloader(s3_bucket, s3_csv_path, s3_client=s3_client, file_name="stnDataCsv.csv")
    
    eg = redShiftUtils.redshift_engine()
    try : 
        s3CsvData.to_sql("weather_stn", eg, index=False, if_exists='replace', schema="raw_data")
        print("DATA = ",s3CsvData)
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    print(redShiftUtils.sql_selecter("SELECT * FROM raw_data.weather_stn"))

weatherStnDataToRedshiftTask = PythonOperator(
    task_id='weatherStnDataToRedshiftTask',
    python_callable=weatherStnDataToRedshift,
    dag=dag,
    queue='queue1'
)


with TaskGroup(group_id='weatherTableSetting', dag=dag) as weatherTableSetting:
    weatherCodeTableCreate = PythonOperator(
        task_id='weatherCodeTableCreate',
        python_callable=weatherCodeTable,
        dag=dag,
        queue='queue1'
    )

    weatherDataTableCreate = PythonOperator(
        task_id='weatherDataTableCreate',
        python_callable=weatherDataTable,
        dag=dag,
        queue='queue1'
    )

    weatherStnTableCreate = PythonOperator(
        task_id='weatherStnTableCreate',
        python_callable=weatherStnTable,
        dag=dag,
        queue='queue1'
    )

# DAG 설정
weatherTableSetting >>  weatherStnDataToRedshiftTask


