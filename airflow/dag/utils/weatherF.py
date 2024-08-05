import requests
import csv
import pandas as pd
import json
from io import StringIO
from utils import redShiftUtils
# 기상청 api 함수

# url 생성기
def apiUrl(domain, options):
    urlstr = ""
    for key, value in options.items() :
        if urlstr != "" :
            urlstr += "&"+key+"="+value
        else :
            urlstr += key+"="+value
    urlstr = domain + urlstr
    return urlstr

# api 호출
def weatherApi(domain, options) :
    apiurl = apiUrl(domain, options)
    print(apiurl)
    response = requests.get(apiurl)
    response.encoding = response.apparent_encoding
    apidata = response.text
    return apidata

# api 데이터 처리후 csv 저장 데이터 구분자 ","
def weatherApiParser(apidata, columns) :
    # Split
    lines = [line for line in apidata.strip().split("\n") if not line.startswith("#")]
    parsed_data = []
    for line in lines:
        parsed_data.append(line.split(","))
    # json 형태로 만들어 return
    json_data = [dict(zip(columns, row)) for row in parsed_data]
    return json_data  


# api 데이터 처리후 csv 저장 데이터 구분자 공백
def weatherApiParser2(apidata, columns) :
    # Split
    lines = [line for line in apidata.strip().split("\n") if not line.startswith("#")]
    parsed_data = []
    for line in lines:
        parsed_data.append(line.split())

    json_data = [dict(zip(columns, row)) for row in parsed_data]
    return json_data  

# api 데이터 처리후 csv 저장
def weatherApiJSONParser(apidata) :
    # json 데이터 받기
    print(apidata)
    data_dict = json.loads(apidata)
    # itme 데이터만 뽑기
    response_data = data_dict["response"]
    itemData = response_data["body"]["items"]["item"]

    return itemData


def weatherCSVmaker(bucket_name, s3_file_path, data, s3_client):
    # 데이터프레임 생성
    df = pd.DataFrame(data)
    
    # CSV 데이터를 메모리 버퍼에 작성
    csv_buffer = StringIO()
    df.to_csv(csv_buffer, index=False)
    
    # S3에 CSV 파일 업로드
    s3_client.put_object(
        Bucket=bucket_name,
        Key=s3_file_path,
        Body=csv_buffer.getvalue(),
        ContentType='text/csv'
    )
    print("Successfully uploaded CSV to S3:", s3_file_path)

def CSVdownloader(bucket_name, s3_file_path, s3_client, file_name):

    # S3에 CSV 파일 다운로드
    obj = s3_client.get_object(
        Bucket=bucket_name, 
        Key=s3_file_path + file_name
    )

    # 데이터프레임 생성
    csv_string = obj['Body'].read().decode('utf-8')
    df = pd.read_csv(StringIO(csv_string), dtype=str)

    print("Successfully download CSV to S3:", s3_file_path+file_name)
    print(df)
    return df

def CSVdownloaderToSpark(bucket_name, s3_file_path, s3_client, file_name, spark):

    # S3에 CSV 파일 다운로드
    obj = s3_client.get_object(
        Bucket=bucket_name, 
        Key=s3_file_path + file_name
    )

    # 데이터프레임 생성
    csv_string = obj['Body'].read().decode('utf-8')
    df = spark.read.csv(StringIO(csv_string), header=True, inferSchema=True)
    
    print("Successfully download CSV to S3:", s3_file_path+file_name)
    print(df)
    return df

def weather_data_create():
    print("run dataTable maker")
    schema = "raw_data"
    drop_sql = f"""DROP TABLE IF EXISTS {schema}.weather_data;"""
    recreate_sql = f"""
CREATE TABLE IF NOT EXISTS {schema}.weather_data (
    baseDate TEXT,
    baseTime TEXT,
    weather_code TEXT,
    fcstDate TEXT,
    fcstTime TEXT,
    fcstValue TEXT,
    nx TEXT,
    ny TEXT
);"""
    sql =[drop_sql,recreate_sql]
    redShiftUtils.sql_execute_to_redshift(sql)

def weather_code_create():
    print("run codeTable maker")
    schema = "raw_data"
    drop_sql = f"""DROP TABLE IF EXISTS {schema}.weather_code;"""
    recreate_sql = f"""
CREATE TABLE IF NOT EXISTS {schema}.weather_code (
    weather_code TEXT PRIMARY KEY,
    weather_code_desc TEXT
);
    """
    sql =[drop_sql,recreate_sql]
    redShiftUtils.sql_execute_to_redshift(sql)

def weather_stn_create():
    print("run stnTable maker")
    schema = "raw_data"
    drop_sql = f"""DROP TABLE IF EXISTS {schema}.weather_stn;"""
    recreate_sql = f"""
CREATE TABLE IF NOT EXISTS {schema}.weather_stn (
    stn TEXT PRIMARY KEY,
    lon TEXT,
    lat TEXT,
    stn_ko TEXT,
    stn_en TEXT
);
    """
    sql =[drop_sql,recreate_sql]
    redShiftUtils.sql_execute_to_redshift(sql)

def weather_merged_df(dfList):
    merged_df = dfList[0]
    for df in dfList[1:]:
        merged_df = merged_df.union(df)

    return merged_df