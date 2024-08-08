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
def weatherX43Y27():
    weatherTask("43", "27")

def weatherX25Y49():
    weatherTask("25", "49")
def weatherX43Y49():
    weatherTask("43", "49")
def weatherX61Y49():
    weatherTask("61", "49")
def weatherX79Y49():
    weatherTask("79", "49")

def weatherX43Y71():
    weatherTask("43", "71")
def weatherX61Y71():
    weatherTask("61", "71")
def weatherX79Y71():
    weatherTask("79", "71")
def weatherX97Y72():
    weatherTask("97", "72")

def weatherX43Y93():
    weatherTask("43", "93")
def weatherX61Y93():
    weatherTask("61", "93")
def weatherX78Y93():
    weatherTask("78", "93")
def weatherX96Y94():
    weatherTask("96", "94")

def weatherX8Y115():
    weatherTask("8", "115")
def weatherX43Y114():
    weatherTask("43", "114")
def weatherX60Y114():
    weatherTask("60", "114")
def weatherX78Y115():
    weatherTask("78", "115")
def weatherX95Y115():
    weatherTask("95", "115")
def weatherX112Y116():
    weatherTask("112", "116")


def weatherX60Y136():
    weatherTask("60", "136")
def weatherX77Y136():
    weatherTask("77", "136")

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
    weatherX43Y27Task = PythonOperator(
        task_id='weatherX43Y27Task',
        python_callable=weatherX43Y27,
        dag=dag,
        queue='queue1'
    )

    weatherX25Y49Task = PythonOperator(
        task_id='weatherX25Y49Task',
        python_callable=weatherX25Y49,
        dag=dag,
        queue='queue1'
    )
    weatherX43Y49Task = PythonOperator(
        task_id='weatherX43Y49Task',
        python_callable=weatherX43Y49,
        dag=dag,
        queue='queue1'
    )
    weatherX61Y49Task = PythonOperator(
        task_id='weatherX61Y49Task',
        python_callable=weatherX61Y49,
        dag=dag,
        queue='queue1'
    )
    weatherX79Y49Task = PythonOperator(
        task_id='weatherX79Y49Task',
        python_callable=weatherX79Y49,
        dag=dag,
        queue='queue1'
    )

    weatherX43Y71Task = PythonOperator(
        task_id='weatherX43Y71Task',
        python_callable=weatherX43Y71,
        dag=dag,
        queue='queue1'
    )
    weatherX61Y71Task = PythonOperator(
        task_id='weatherX61Y71Task',
        python_callable=weatherX61Y71,
        dag=dag,
        queue='queue1'
    )
    weatherX79Y71Task = PythonOperator(
        task_id='weatherX79Y71Task',
        python_callable=weatherX79Y71,
        dag=dag,
        queue='queue1'
    )
    weatherX97Y72Task = PythonOperator(
        task_id='weatherX97Y72Task',
        python_callable=weatherX97Y72,
        dag=dag,
        queue='queue1'
    )

    weatherX43Y93Task = PythonOperator(
        task_id='weatherX43Y93Task',
        python_callable=weatherX43Y93,
        dag=dag,
        queue='queue1'
    )
    weatherX61Y93Task = PythonOperator(
        task_id='weatherX61Y93Task',
        python_callable=weatherX61Y93,
        dag=dag,
        queue='queue1'
    )
    weatherX78Y93Task = PythonOperator(
        task_id='weatherX78Y93Task',
        python_callable=weatherX78Y93,
        dag=dag,
        queue='queue1'
    )
    weatherX96Y94Task = PythonOperator(
        task_id='weatherX96Y94Task',
        python_callable=weatherX96Y94,
        dag=dag,
        queue='queue1'
    )

    weatherX8Y115Task = PythonOperator(
        task_id='weatherX8Y115Task',
        python_callable=weatherX8Y115,
        dag=dag,
        queue='queue1'
    )
    weatherX43Y114Task = PythonOperator(
        task_id='weatherX43Y114Task',
        python_callable=weatherX43Y114,
        dag=dag,
        queue='queue1'
    )
    weatherX60Y114Task = PythonOperator(
        task_id='weatherX60Y114Task',
        python_callable=weatherX60Y114,
        dag=dag,
        queue='queue1'
    )
    weatherX78Y115Task = PythonOperator(
        task_id='weatherX78Y115Task',
        python_callable=weatherX78Y115,
        dag=dag,
        queue='queue1'
    )
    weatherX95Y115Task = PythonOperator(
        task_id='weatherX95Y115Task',
        python_callable=weatherX95Y115,
        dag=dag,
        queue='queue1'
    )
    weatherX112Y116Task = PythonOperator(
        task_id='weatherX112Y116Task',
        python_callable=weatherX112Y116,
        dag=dag,
        queue='queue1'
    )

    weatherX60Y136Task = PythonOperator(
        task_id='weatherX60Y136Task',
        python_callable=weatherX60Y136,
        dag=dag,
        queue='queue1'
    )
    weatherX77Y136Task = PythonOperator(
        task_id='weatherX77Y136Task',
        python_callable=weatherX77Y136,
        dag=dag,
        queue='queue1'
    )
    weatherX43Y27Task >> weatherX25Y49Task >> weatherX43Y49Task >> weatherX61Y49Task >> weatherX79Y49Task >> weatherX43Y71Task >> weatherX61Y71Task >> weatherX79Y71Task >> weatherX97Y72Task >> weatherX43Y93Task >> weatherX61Y93Task >> weatherX78Y93Task >> weatherX96Y94Task >> weatherX8Y115Task >> weatherX43Y114Task >> weatherX60Y114Task >> weatherX78Y115Task >> weatherX95Y115Task >> weatherX112Y116Task >> weatherX60Y136Task >> weatherX77Y136Task
    
CsvToSql = PythonOperator(
        task_id='CsvToSql',
        python_callable=weatherCsvToSql,
        dag=dag,
        queue='queue1'
    )
# DAG 설정
CSVSetting >> CsvToSql

