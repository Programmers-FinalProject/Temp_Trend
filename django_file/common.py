import pandas as pd
import json
from io import StringIO

def csv_to_json(csv_file_path):
    # CSV 파일 읽기
    df = pd.read_csv(csv_file_path)

    # DataFrame을 JSON 포맷으로 변환
   
# category_raw_data
# 많이추움 -60,추움 - 20,쌀쌀함 0,따뜻함 10,더움 37,많이더움 60,비 1 4 = 1,눈 2 3 = 2

# json으로 반환
def S3_CSVdownloader(bucket_name, s3_file_path, s3_client, file_name):
    # S3에 CSV 파일 다운로드
    obj = s3_client.get_object(
        Bucket=bucket_name, 
        Key=s3_file_path + file_name
    )

    # 데이터프레임 생성
    csv_string = obj['Body'].read().decode('utf-8')
    df = pd.read_csv(StringIO(csv_string), dtype=str, skiprows=1, header=None)

    json_data = df.to_json(orient='records', force_ascii=False, indent=4)
    return json_data

# dict 구조 - cate : {hightmp:,lowtmp:,we:}
def main():
    # CSV 파일 읽기
    df = pd.read_csv('category_raw_data.csv')
    print("test")
    # DataFrame을 JSON 포맷으로 변환
    csvJson = json.loads(df.to_json(orient='records', force_ascii=False, indent=4))
    cols = {'tmp1':-60,'tmp2':-20,'tmp3':0,'tmp4':10,'tmp5':37,'tmp6':60,'we1':1,'we2':2}

    newdict = {}
    for row in csvJson :
        for key,item in row.items() :
            if key in cols.keys()
            if newdict[item] :
                print(key,":",item)    
            else :
                newdict[item] = newdict[item]
            
    result = csvJson
    return result

if __name__ == '__main__':
    main()
