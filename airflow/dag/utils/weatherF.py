import requests
import csv
import pandas as pd
import json
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

def weatherCSVmaker(path, fileName, data):
    df = pd.DataFrame(data)
    csv_file_path = path + fileName
    df.to_csv(csv_file_path, index=False)
    
    print("write CSV on ",path,fileName,sep="")