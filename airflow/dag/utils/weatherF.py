import requests
import csv
import pandas as pd
import json
from io import StringIO
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