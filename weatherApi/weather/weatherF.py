import requests
import csv
import json
from pyspark.sql import SparkSession

# path = 아마 s3 폴더위치로 사용할듯 싶음 or csv로 저장하지않고 바로 db에 넣거나
path = "dataPipeline/data/"
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
def weatherApi(apiurl) :
    response = requests.get(apiurl)
    response.encoding = response.apparent_encoding
    apidata = response.text
    return apidata

# api 데이터 처리후 csv 저장
def weatherApiParser(apidata, columns ,fileName) :
    # Split
    lines = [line for line in apidata.strip().split("\n") if not line.startswith("#")]
    parsed_data = []
    for line in lines:
        parsed_data.append(line.split(","))
    # json 형태로 만들어 return
    json_data = [dict(zip(columns, row)) for row in parsed_data]
    return json_data  
    # CSV쓰기
    # with open(path + fileName, 'w', newline='',encoding='utf-8') as csvfile:
    #     csvwriter = csv.writer(csvfile)
    #     csvwriter.writerow(columns)
    #     csvwriter.writerows(parsed_data)

    # print("write ",path,fileName,sep="")

# api 데이터 처리후 csv 저장
def weatherApiJSONParser(apidata) :
    # json 데이터 받기
    data_dict = json.loads(apidata)
    # itme 데이터만 뽑기
    response_data = data_dict["response"]
    itemData = response_data["body"]["items"]["item"]

    return itemData

    # # spark 세션 빌드
    # spark = SparkSession.builder \
    #     .appName("JSON to DataFrame") \
    #     .getOrCreate()
    # # dataframe 만듬
    # df = spark.createDataFrame(itemData)
    # df.show()