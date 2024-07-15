import weatherF 
# api 계정 정보 - 남은 api 통신 가능데이터량 확인하고싶으면 접속해보면됨
# https://apihub.kma.go.kr/ 주소
# dkswodud0531@gmail.com
# admin123!@#

# 변수 선언 - Variables으로 처리할듯?
# 기상청 지점 api col
StnColumns = ["STN","LON","LAT","STN_SP","HT","HT_PA","HT_TA","HT_WD","HT_RN","STN","STN_KO","STN_EN","FCT_ID",
            "LAW_ID","BASIN"]
# 기상청 날씨정보 api col
DataColumns = ["TM", "STN", "WS_AVG", "WR_DAY", "WD_MAX", "WS_MAX", "WS_MAX_TM", "WD_INS", "WS_INS", "WS_INS_TM",
            "TA_AVG", "TA_MAX", "TA_MAX_TM", "TA_MIN", "TA_MIN_TM", "TD_AVG", "TS_AVG", "TG_MIN", "HM_AVG", "HM_MIN",
            "HM_MIN_TM", "PV_AVG", "EV_S", "EV_L", "FG_DUR", "PA_AVG", "PS_AVG", "PS_MAX", "PS_MAX_TM", "PS_MIN",
            "PS_MIN_TM", "CA_TOT", "SS_DAY", "SS_DUR", "SS_CMB", "SI_DAY", "SI_60M_MAX", "SI_60M_MAX_TM", "RN_DAY",
            "RN_D99", "RN_DUR", "RN_60M_MAX", "RN_60M_MAX_TM", "RN_10M_MAX", "RN_10M_MAX_TM", "RN_POW_MAX", 
            "RN_POW_MAX_TM", "SD_NEW", "SD_NEW_TM", "SD_MAX", "SD_MAX_TM", "TE_05", "TE_10", "TE_15", "TE_30", "TE_50"]
# csv 파일 이름
dataFileName = "weather_data.csv"
dataStnFileName = 'weather_stn.csv'
# api 도메인
domain = "https://apihub.kma.go.kr/api/typ01/url/kma_sfctm2.php?"
Stndomain = "https://apihub.kma.go.kr/api/typ01/url/stn_inf.php?"
# path = "data/" # csv 파일 저장 path
# api 보안키
auth = "_T8QbW2dT_-_EG1tna__OQ"
apiStnOption = {
    "tm" : "",
    "stn" : "",
    "inf" : 'SFC',
    "help" : '0',
    "authKey" : auth,
}

apiOption = {
    "tm" : "",
    "stn" : "",
    "disp" : '0',
    "help" : '0',
    "authKey" : auth,
}

# 기상청 지점 정보
# 필요 반복 횟수 - 파이프라인 생성시 한번
apiurl = weatherF.apiUrl(Stndomain, apiOption)  
weatherF.weatherApiParser(weatherF.weatherApi(apiurl), columns=StnColumns, fileName=dataStnFileName)
# 전국 현재날씨 정보
# 필요 반복 횟수 - 매시간마다 시간마다 1번
apiurl = weatherF.apiUrl(domain, apiOption)  
weatherF.weatherApiParser(weatherF.weatherApi(apiurl), columns=DataColumns, fileName=dataFileName)