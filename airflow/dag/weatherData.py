import time
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.models import Variable
from airflow.utils.task_group import TaskGroup
from datetime import datetime, timedelta
from utils import weatherF, redShiftUtils, nxny
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
    schedule_interval='20 20 * * *',
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
def weatherX60Y127():
    weatherTask("60", "127")
def weatherX21Y135():
    weatherTask("21", "135")
def weatherX60Y121():
    weatherTask("60", "121")
def weatherX73Y134():
    weatherTask("73", "134")
def weatherX92Y131():
    weatherTask("92", "131")
def weatherX69Y106():
    weatherTask("69", "106")
def weatherX67Y100():
    weatherTask("67", "100")
def weatherX63Y89():
    weatherTask("63", "89")
def weatherX58Y74():
    weatherTask("58", "74")
def weatherX50Y67():
    weatherTask("50", "67")
def weatherX127Y127():
    weatherTask("127", "127")
def weatherX91Y106():
    weatherTask("91", "106")
def weatherX89Y90():
    weatherTask("89", "90")

def weatherX102Y84():
    weatherTask("102", "84")
def weatherX98Y76():
    weatherTask("98", "76")
def weatherX52Y38():
    weatherTask("52", "38")

def weatherCsvToSql():
    sql = "SELECT left(lat,2) nx, left(lon,3) ny FROM raw_data.weather_stn GROUP BY left(lat,2), left(lon,3) ORDER BY left(lat,2), left(lon,3)"
    xydf = redShiftUtils.sql_selecter(sql)
    xyjson = xydf.to_json(orient="records")
    xyjson = json.loads(xyjson)
    csvDf = pd.DataFrame()
    for xy in xyjson :
        nxnypos = nxny.nxnySetting(lon=int(xy['ny']), lat=int(xy['nx']))
        s3CsvData = weatherF.CSVdownloader(s3_bucket, s3_csv_path, s3_client=s3_client, file_name=f"weatherAPIData_{nxnypos['nx']}_{nxnypos['ny']}.csv")
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
    weatherX60Y127Task = PythonOperator(
        task_id='weatherX60Y127Task',
        python_callable=weatherX60Y127,
        dag=dag,
        queue='queue1'
    )

    weatherX21Y135Task = PythonOperator(
        task_id='weatherX21Y135Task',
        python_callable=weatherX21Y135,
        dag=dag,
        queue='queue1'
    )
    weatherX60Y121Task = PythonOperator(
        task_id='weatherX60Y121Task',
        python_callable=weatherX60Y121,
        dag=dag,
        queue='queue1'
    )
    weatherX73Y134Task = PythonOperator(
        task_id='weatherX73Y134Task',
        python_callable=weatherX73Y134,
        dag=dag,
        queue='queue1'
    )
    weatherX92Y131Task = PythonOperator(
        task_id='weatherX92Y131Task',
        python_callable=weatherX92Y131,
        dag=dag,
        queue='queue1'
    )

    weatherX69Y106Task = PythonOperator(
        task_id='weatherX69Y106Task',
        python_callable=weatherX69Y106,
        dag=dag,
        queue='queue1'
    )
    weatherX67Y100Task = PythonOperator(
        task_id='weatherX67Y100Task',
        python_callable=weatherX67Y100,
        dag=dag,
        queue='queue1'
    )
    weatherX63Y89Task = PythonOperator(
        task_id='weatherX63Y89Task',
        python_callable=weatherX63Y89,
        dag=dag,
        queue='queue1'
    )
    weatherX58Y74Task = PythonOperator(
        task_id='weatherX58Y74Task',
        python_callable=weatherX58Y74,
        dag=dag,
        queue='queue1'
    )

    weatherX50Y67Task = PythonOperator(
        task_id='weatherX50Y67Task',
        python_callable=weatherX50Y67,
        dag=dag,
        queue='queue1'
    )
    weatherX127Y127Task = PythonOperator(
        task_id='weatherX127Y127Task',
        python_callable=weatherX127Y127,
        dag=dag,
        queue='queue1'
    )
    weatherX91Y106Task = PythonOperator(
        task_id='weatherX91Y106Task',
        python_callable=weatherX91Y106,
        dag=dag,
        queue='queue1'
    )
    weatherX89Y90Task = PythonOperator(
        task_id='weatherX89Y90Task',
        python_callable=weatherX89Y90,
        dag=dag,
        queue='queue1'
    )

    weatherX102Y84Task = PythonOperator(
        task_id='weatherX102Y84Task',
        python_callable=weatherX102Y84,
        dag=dag,
        queue='queue1'
    )
    weatherX98Y76Task = PythonOperator(
        task_id='weatherX98Y76Task',
        python_callable=weatherX98Y76,
        dag=dag,
        queue='queue1'
    )
    weatherX52Y38Task = PythonOperator(
        task_id='weatherX52Y38Task',
        python_callable=weatherX52Y38,
        dag=dag,
        queue='queue1'
    )
    
    weatherX60Y127Task >> weatherX21Y135Task >> weatherX60Y121Task >> weatherX73Y134Task >> weatherX92Y131Task >> weatherX69Y106Task >> weatherX67Y100Task >> weatherX63Y89Task >> weatherX58Y74Task >> weatherX50Y67Task >> weatherX127Y127Task >> weatherX91Y106Task >> weatherX89Y90Task >> weatherX102Y84Task >> weatherX98Y76Task >> weatherX52Y38Task
    
CsvToSql = PythonOperator(
        task_id='CsvToSql',
        python_callable=weatherCsvToSql,
        dag=dag,
        queue='queue1'
    )
# DAG 설정
CSVSetting >> CsvToSql

