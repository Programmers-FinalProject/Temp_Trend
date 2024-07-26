import time
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.models import Variable
from airflow.utils.task_group import TaskGroup
from datetime import datetime, timedelta
from utils import weatherF
from utils import redShiftUtils
import boto3, json, psycopg2
import pandas as pd

s3_client = boto3.client(
    's3',
    aws_access_key_id =  Variable.get("ACCESS_KEY"),
    aws_secret_access_key = Variable.get("SECRET_KEY"),
)
s3_bucket = Variable.get("s3_bucket")
s3_csv_path = Variable.get("we_s3_csv_path")
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
    start_date=datetime(2024, 7, 26),
    catchup=False,
)

def weatherTask(nx,ny):
    weApiOption["nx"] = nx
    weApiOption["ny"] = ny

    apidata = weatherF.weatherApiJSONParser(weatherF.weatherApi(Variable.get("weDomain"), weApiOption))
    print(apidata)
    weatherF.weatherCSVmaker(s3_bucket, f"{s3_csv_path}weatherAPIData_{weApiOption['nx']}_{weApiOption['ny']}.csv",apidata, s3_client)
    print(f"weatherAPIData_{weApiOption['nx']}_{weApiOption['ny']} Save")
    time.sleep(5)

# 작업 함수 정의
def weatherX33Y126():
    weatherTask("33", "126")

def weatherX34Y125():
    weatherTask("34", "125")
def weatherX34Y126():
    weatherTask("34", "126")
def weatherX34Y127():
    weatherTask("34", "127")
def weatherX34Y128():
    weatherTask("34", "128")

def weatherX35Y126():
    weatherTask("35", "126")
def weatherX35Y127():
    weatherTask("35", "127")
def weatherX35Y128():
    weatherTask("35", "128")
def weatherX35Y129():
    weatherTask("35", "129")

def weatherX36Y126():
    weatherTask("36", "126")
def weatherX36Y127():
    weatherTask("36", "127")
def weatherX36Y128():
    weatherTask("36", "128")
def weatherX36Y129():
    weatherTask("36", "129")

def weatherX37Y124():
    weatherTask("37", "124")
def weatherX37Y126():
    weatherTask("37", "126")
def weatherX37Y127():
    weatherTask("37", "127")
def weatherX37Y128():
    weatherTask("37", "128")
def weatherX37Y129():
    weatherTask("37", "129")
def weatherX37Y130():
    weatherTask("37", "130")


def weatherX38Y127():
    weatherTask("38", "127")
def weatherX38Y128():
    weatherTask("38", "128")

def weatherCsvToSql():
    sql = "SELECT left(lat,2) nx, left(lon,3) ny FROM raw_data.weather_stn GROUP BY left(lat,2), left(lon,3) ORDER BY left(lat,2), left(lon,3)"
    xydf = redShiftUtils.sql_selecter(sql)
    xyjson = xydf.to_json(orient="records")
    xyjson = json.loads(xyjson)
    csvDf = pd.DataFrame()
    for xy in xyjson :
        s3CsvData = weatherF.CSVdownloader(s3_bucket, s3_csv_path, s3_client=s3_client, file_name=f"weatherAPIData_{xy['nx']}_{xy['ny']}.csv")
        csvDf = pd.concat([csvDf, s3CsvData], ignore_index=True)
    csvDf = dataAsType(csvDf)
    print("csv",csvDf)
    redshiftData = redShiftUtils.sql_selecter("SELECT * FROM raw_data.weather_data")
    merged_data = pd.concat([csvDf, redshiftData], ignore_index=True)

    eg = redShiftUtils.redshift_engine()
    try : 
        merged_data.to_sql("weather_data", eg, index=False, if_exists='append', schema="raw_data", )
        print("DATA = ",merged_data)
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    print(redShiftUtils.sql_selecter("SELECT * FROM raw_data.weather_data"))

def dataAsType(df):
    df = df.rename(columns={
    'baseDate': 'basedate',
    'baseTime': 'basetime',
    'category': 'weather_code',
    'fcstDate': 'fcstdate',
    'fcstTime': 'fcsttime',
    'fcstValue': 'fcstvalue'
})
    return df

with TaskGroup(group_id='weatherTableSetting', dag=dag) as CSVSetting:
    # PythonOperator를 사용하여 작업 정의
    weatherX33Y126Task = PythonOperator(
        task_id='weatherX33Y126Task',
        python_callable=weatherX33Y126,
        dag=dag,
    )

    weatherX34Y125Task = PythonOperator(
        task_id='weatherX34Y125Task',
        python_callable=weatherX34Y125,
        dag=dag,
    )
    weatherX34Y126Task = PythonOperator(
        task_id='weatherX34Y126Task',
        python_callable=weatherX34Y126,
        dag=dag,
    )
    weatherX34Y127Task = PythonOperator(
        task_id='weatherX34Y127Task',
        python_callable=weatherX34Y127,
        dag=dag,
    )
    weatherX34Y128Task = PythonOperator(
        task_id='weatherX34Y128Task',
        python_callable=weatherX34Y128,
        dag=dag,
    )

    weatherX35Y126Task = PythonOperator(
        task_id='weatherX35Y126Task',
        python_callable=weatherX35Y126,
        dag=dag,
    )
    weatherX35Y127Task = PythonOperator(
        task_id='weatherX35Y127Task',
        python_callable=weatherX35Y127,
        dag=dag,
    )
    weatherX35Y128Task = PythonOperator(
        task_id='weatherX35Y128Task',
        python_callable=weatherX35Y128,
        dag=dag,
    )
    weatherX35Y129Task = PythonOperator(
        task_id='weatherX35Y129Task',
        python_callable=weatherX35Y129,
        dag=dag,
    )

    weatherX36Y126Task = PythonOperator(
        task_id='weatherX36Y126Task',
        python_callable=weatherX36Y126,
        dag=dag,
    )
    weatherX36Y127Task = PythonOperator(
        task_id='weatherX36Y127Task',
        python_callable=weatherX36Y127,
        dag=dag,
    )
    weatherX36Y128Task = PythonOperator(
        task_id='weatherX36Y128Task',
        python_callable=weatherX36Y128,
        dag=dag,
    )
    weatherX36Y129Task = PythonOperator(
        task_id='weatherX36Y129Task',
        python_callable=weatherX36Y129,
        dag=dag,
    )

    weatherX37Y124Task = PythonOperator(
        task_id='weatherX37Y124Task',
        python_callable=weatherX37Y124,
        dag=dag,
    )
    weatherX37Y126Task = PythonOperator(
        task_id='weatherX37Y126Task',
        python_callable=weatherX37Y126,
        dag=dag,
    )
    weatherX37Y127Task = PythonOperator(
        task_id='weatherX37Y127Task',
        python_callable=weatherX37Y127,
        dag=dag,
    )
    weatherX37Y128Task = PythonOperator(
        task_id='weatherX37Y128Task',
        python_callable=weatherX37Y128,
        dag=dag,
    )
    weatherX37Y129Task = PythonOperator(
        task_id='weatherX37Y129Task',
        python_callable=weatherX37Y129,
        dag=dag,
    )
    weatherX37Y130Task = PythonOperator(
        task_id='weatherX37Y130Task',
        python_callable=weatherX37Y130,
        dag=dag,
    )

    weatherX38Y127Task = PythonOperator(
        task_id='weatherX38Y127Task',
        python_callable=weatherX38Y127,
        dag=dag,
    )
    weatherX38Y128Task = PythonOperator(
        task_id='weatherX38Y128Task',
        python_callable=weatherX38Y128,
        dag=dag,
    )

CsvToSql = PythonOperator(
        task_id='CsvToSql',
        python_callable=weatherCsvToSql,
        dag=dag,
    )
# DAG 설정
CSVSetting >> CsvToSql

