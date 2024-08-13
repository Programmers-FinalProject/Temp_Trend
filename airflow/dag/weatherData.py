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

LOCATIONS = [
    {'name': '서울', 'nx': 60, 'ny': 127, 'zone': 'z1'},
    {'name': '백령도', 'nx': 21, 'ny': 135, 'zone': 'z2'},
    {'name': '수원', 'nx': 60, 'ny': 121, 'zone': 'z3'},  # 수원도 서울과 같은 nx, ny를 사용
    {'name': '춘천', 'nx': 73, 'ny': 134, 'zone': 'z4'},
    {'name': '강릉', 'nx': 92, 'ny': 131, 'zone': 'z5'},
    {'name': '청주', 'nx': 69, 'ny': 106, 'zone': 'z6'},
    {'name': '대전', 'nx': 67, 'ny': 100, 'zone': 'z7'},
    {'name': '전주', 'nx': 63, 'ny': 89, 'zone': 'z8'},
    {'name': '광주', 'nx': 58, 'ny': 74, 'zone': 'z9'},
    {'name': '목포', 'nx': 50, 'ny': 67, 'zone': 'z10'},
    {'name': '여수', 'nx': 73, 'ny': 66, 'zone': 'z11'},
    {'name': '울릉도', 'nx': 127, 'ny': 127, 'zone': 'z12'},
    {'name': '안동', 'nx': 91, 'ny': 106, 'zone': 'z13'},
    {'name': '대구', 'nx': 89, 'ny': 90, 'zone': 'z14'},
    {'name': '울산', 'nx': 102, 'ny': 84, 'zone': 'z15'},
    {'name': '부산', 'nx': 98, 'ny': 76, 'zone': 'z16'},
    {'name': '제주', 'nx': 52, 'ny': 38, 'zone': 'z17'},
]



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
def weatherX73Y66():
    weatherTask("73", "66")
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
def weatherX87Y106():
    weatherTask("87", "106")
def weatherX60Y120():
    weatherTask("60", "120")
def weatherX91Y77():
    weatherTask("91", "77")
def weatherX66Y103():
    weatherTask("66", "103")
def weatherX55Y124():
    weatherTask("55", "124")
def weatherX51Y67():
    weatherTask("51", "67")
def weatherX28Y8():
    weatherTask("28", "8")
def weatherX68Y100():
    weatherTask("68", "100")
def weatherX69Y107():
    weatherTask("69", "107")


# 특수성 있는 지역들
weather_nxny = [
    {"nx": 21 , "ny": 135},
    {"nx": 60 , "ny": 121},
    {"nx": 92 , "ny": 131},
    {"nx": 69 , "ny": 106},
    {"nx": 50 , "ny": 67},
    {"nx": 73 , "ny": 66},
    {"nx": 127 , "ny": 127},
    {"nx": 91 , "ny": 106},
]

def weatherCsvToSql():
    sql = "SELECT nx, ny FROM ( SELECT location2, location3, location1, nx, ny, ROW_NUMBER() OVER (PARTITION BY location1 ORDER BY location1) AS row_num FROM raw_data.weather_stn) AS count WHERE row_num = 1 ORDER BY location2 DESC, location3 DESC"
    xydf = redShiftUtils.sql_selecter(sql)
    xyjson = xydf.to_json(orient="records")
    xyjson = json.loads(xyjson)
    xyjson = xyjson + weather_nxny
    csvDf = pd.DataFrame()
    for xy in xyjson :
        nxnypos = nxny.nxnySetting(lon=int(xy['ny']), lat=int(xy['nx']))
        s3CsvData = weatherF.CSVdownloader(s3_bucket, s3_csv_path, s3_client=s3_client, file_name=f"weatherAPIData_{nxnypos['nx']}_{nxnypos['ny']}.csv")
        csvDf = pd.concat([csvDf, s3CsvData], ignore_index=True)
    csvDf = dataAsType(csvDf)
    print("csv",csvDf)

    eg = redShiftUtils.redshift_engine()
    try : 
        csvDf.to_sql("weather_data", eg, index=False, if_exists='replace', schema="raw_data", )
        print("저장완료", redShiftUtils.sql_selecter("SELECT * FROM raw_data.weather_data limit 10"))
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)

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
    # 서울
    weatherX60Y127Task = PythonOperator(
        task_id='weatherX60Y127Task',
        python_callable=weatherX60Y127,
        dag=dag,
        queue='queue1'
    )
    # 백령도
    weatherX21Y135Task = PythonOperator(
        task_id='weatherX21Y135Task',
        python_callable=weatherX21Y135,
        dag=dag,
        queue='queue1'
    )
    # 수원
    weatherX60Y121Task = PythonOperator(
        task_id='weatherX60Y121Task',
        python_callable=weatherX60Y121,
        dag=dag,
        queue='queue1'
    )
    # 춘천 
    weatherX73Y134Task = PythonOperator(
        task_id='weatherX73Y134Task',
        python_callable=weatherX73Y134,
        dag=dag,
        queue='queue1'
    )
    # 강릉
    weatherX92Y131Task = PythonOperator(
        task_id='weatherX92Y131Task',
        python_callable=weatherX92Y131,
        dag=dag,
        queue='queue1'
    )
    # 청주
    weatherX69Y106Task = PythonOperator(
        task_id='weatherX69Y106Task',
        python_callable=weatherX69Y106,
        dag=dag,
        queue='queue1'
    )
    # 대전
    weatherX67Y100Task = PythonOperator(
        task_id='weatherX67Y100Task',
        python_callable=weatherX67Y100,
        dag=dag,
        queue='queue1'
    )
    # 전주
    weatherX63Y89Task = PythonOperator(
        task_id='weatherX63Y89Task',
        python_callable=weatherX63Y89,
        dag=dag,
        queue='queue1'
    )
    # 광주
    weatherX58Y74Task = PythonOperator(
        task_id='weatherX58Y74Task',
        python_callable=weatherX58Y74,
        dag=dag,
        queue='queue1'
    )
    # 목포
    weatherX50Y67Task = PythonOperator(
        task_id='weatherX50Y67Task',
        python_callable=weatherX50Y67,
        dag=dag,
        queue='queue1'
    )
    # 여수
    weatherX73Y66Task = PythonOperator(
        task_id='weatherX73Y66Task',
        python_callable=weatherX73Y66,
        dag=dag,
        queue='queue1'
    )
    # 울릉도
    weatherX127Y127Task = PythonOperator(
        task_id='weatherX127Y127Task',
        python_callable=weatherX127Y127,
        dag=dag,
        queue='queue1'
    )
    # 안동
    weatherX91Y106Task = PythonOperator(
        task_id='weatherX91Y106Task',
        python_callable=weatherX91Y106,
        dag=dag,
        queue='queue1'
    )
    # 대구
    weatherX89Y90Task = PythonOperator(
        task_id='weatherX89Y90Task',
        python_callable=weatherX89Y90,
        dag=dag,
        queue='queue1'
    )
    # 울산
    weatherX102Y84Task = PythonOperator(
        task_id='weatherX102Y84Task',
        python_callable=weatherX102Y84,
        dag=dag,
        queue='queue1'
    )
    # 부산
    weatherX98Y76Task = PythonOperator(
        task_id='weatherX98Y76Task',
        python_callable=weatherX98Y76,
        dag=dag,
        queue='queue1'
    )
    # 제주
    weatherX52Y38Task = PythonOperator(
        task_id='weatherX52Y38Task',
        python_callable=weatherX52Y38,
        dag=dag,
        queue='queue1'
    )
    # 경북
    weatherX87Y106Task = PythonOperator(
        task_id='weatherX87Y106Task',
        python_callable=weatherX87Y106,
        dag=dag,
        queue='queue1'
    )
    # 경기
    weatherX60Y120Task = PythonOperator(
        task_id='weatherX60Y120Task',
        python_callable=weatherX60Y120,
        dag=dag,
        queue='queue1'
    )
    # 경남
    weatherX91Y77Task = PythonOperator(
        task_id='weatherX91Y77Task',
        python_callable=weatherX91Y77,
        dag=dag,
        queue='queue1'
    )
    # 세종
    weatherX66Y103Task = PythonOperator(
        task_id='weatherX66Y103Task',
        python_callable=weatherX66Y103,
        dag=dag,
        queue='queue1'
    )
    # 인천
    weatherX55Y124Task = PythonOperator(
        task_id='weatherX55Y124Task',
        python_callable=weatherX55Y124,
        dag=dag,
        queue='queue1'
    )
    # 전남
    weatherX51Y67Task = PythonOperator(
        task_id='weatherX51Y67Task',
        python_callable=weatherX51Y67,
        dag=dag,
        queue='queue1'
    )
    # 이어도
    weatherX28Y8Task = PythonOperator(
        task_id='weatherX28Y8Task',
        python_callable=weatherX28Y8,
        dag=dag,
        queue='queue1'
    )
    # 충남 
    weatherX68Y100Task = PythonOperator(
        task_id='weatherX68Y100Task',
        python_callable=weatherX68Y100,
        dag=dag,
        queue='queue1'
    )
    # 충북
    weatherX69Y107Task = PythonOperator(
        task_id='weatherX69Y107Task',
        python_callable=weatherX69Y107,
        dag=dag,
        queue='queue1'
    )

    weatherX60Y127Task >> weatherX21Y135Task >> weatherX60Y121Task >> weatherX73Y134Task >> weatherX92Y131Task >> weatherX69Y106Task >> weatherX67Y100Task >> weatherX63Y89Task >> weatherX58Y74Task >> weatherX50Y67Task >> weatherX127Y127Task >> weatherX91Y106Task >> weatherX89Y90Task >> weatherX102Y84Task >> weatherX98Y76Task >> weatherX52Y38Task >> weatherX87Y106Task >> weatherX60Y120Task >> weatherX66Y103Task >> weatherX55Y124Task >> weatherX51Y67Task >> weatherX28Y8Task >> weatherX68Y100Task >> weatherX69Y107Task >> weatherX73Y66Task >> weatherX91Y77Task
    
CsvToSql = PythonOperator(
        task_id='CsvToSql',
        python_callable=weatherCsvToSql,
        dag=dag,
        queue='queue1'
    )
# DAG 설정
CSVSetting >> CsvToSql

