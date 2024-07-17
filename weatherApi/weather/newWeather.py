import requests
from datetime import datetime
import weatherF 
# api 계정 정보 - 남은 api 통신 가능데이터량 확인하고싶으면 접속해보면됨
# https://apihub.kma.go.kr/ 주소
# dkswodud0531@gmail.com
# admin123!@#
# 현재 시간 가져오기

now = datetime.now()
today = now.strftime('%Y%m%d')
today = today
auth = "_T8QbW2dT_-_EG1tna__OQ"
serviceKey = "N%2F5IvyGJ3gEEmCKXFXrptjV6frUA4rbVq9oCvBv%2FQ%2F4J6vD%2Bigor3OzhxgNauxyp4k0jJyyHPo%2FC7EbbQCO1XA%3D%3D"
numOfRows = "10000"
domain = "https://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getVilageFcst?"
apiOption = {
    "serviceKey" : serviceKey,
    "numOfRows" : numOfRows,
    "pageNo" : '1',
    "dataType" : 'json',
    "base_date" : today,
    "base_time" : "1100"
}

stnDomain = "https://apihub.kma.go.kr/api/typ01/url/stn_inf.php?"
stnColumns = ["STN","LON","LAT","STN_SP","HT","HT_PA","HT_TA","HT_WD","HT_RN","STN","STN_KO","STN_EN","FCT_ID",
            "LAW_ID","BASIN"]
stnOption = {
    "inf":"SFC",
    "authKey" : auth,
}
# stnurl = weatherF.apiUrl(stnDomain, stnOption)
# stnData = weatherF.weatherApiParser2(weatherF.weatherApi(stnurl), columns=stnColumns, fileName="test.csv")

response = requests.get(domain, verify=True)  # Remove the ssl_version argument
apidata = response.text
