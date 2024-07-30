from django.shortcuts import render
from datetime import datetime, timedelta
from weather.models import WeatherData

def we_data_test(request):
    # test = WeatherData.objects.using('redshift').all()
    test = [{'baseDate': '20240729', 'baseTime': '0500', 'category': 'TMP', 'fcstDate': '20240729', 'fcstTime': '0600', 'fcstValue': '26', 'nx': '34', 'ny': '126'}, {'baseDate': '20240729', 'baseTime': '0500', 'category': 'UUU', 'fcstDate': '20240729', 'fcstTime': '0600', 'fcstValue': '5.5', 'nx': '34', 'ny': '126'}, {'baseDate': '20240729', 'baseTime': '0500', 'category': 'VVV', 'fcstDate': '20240729', 'fcstTime': '0600', 'fcstValue': '6.6', 'nx': '34', 'ny': '126'}, {'baseDate': '20240729', 'baseTime': '0500', 'category': 'VEC', 'fcstDate': '20240729', 'fcstTime': '0600', 'fcstValue': '220', 'nx': '34', 'ny': '126'}, {'baseDate': '20240729', 'baseTime': '0500', 'category': 'WSD', 'fcstDate': '20240729', 'fcstTime': '0600', 'fcstValue': '8.6', 'nx': '34', 'ny': '126'}, {'baseDate': '20240729', 'baseTime': '0500', 'category': 'SKY', 'fcstDate': '20240729', 'fcstTime': '0600', 'fcstValue': '3', 'nx': '34', 'ny': '126'}, {'baseDate': '20240729', 'baseTime': '0500', 'category': 'PTY', 'fcstDate': '20240729', 'fcstTime': '0600', 'fcstValue': '0', 'nx': '34', 'ny': '126'}, {'baseDate': '20240729', 'baseTime': '0500', 'category': 'POP', 'fcstDate': '20240729', 'fcstTime': '0600', 'fcstValue': '20', 'nx': '34', 'ny': '126'}, {'baseDate': '20240729', 'baseTime': '0500', 'category': 'WAV', 'fcstDate': '20240729', 'fcstTime': '0600', 'fcstValue': '2', 'nx': '34', 'ny': '126'}, {'baseDate': '20240729', 'baseTime': '0500', 'category': 'PCP', 'fcstDate': '20240729', 'fcstTime': '0600', 'fcstValue': '강수없음', 'nx': '34', 'ny': '126'}]
    context = {'we-dataList' : we_data_setting(test)}
    return render(request, 'wedatatest.html', context)

# 예보날짜 세팅
def based_ymdgetter():
    now = datetime.now()

    # 05시 30분 이전은 어제 예보 정보를 가지고 결과 보여줌
    hm = now.strftime("%H%M")
    ckhm = datetime.strptime("0530", "%H%M")
    if(hm < ckhm) :
        now = now - timedelta(days=1)

    ymd = now.strftime("%Y%m%d")
    return ymd

def ymd_timegetter():
    pdict = {}
    now = datetime.now()
    ymd = now.strftime("%Y%m%d")
    hm = now.strftime("%H00")
    pdict["Pfcstdate"] = ymd
    pdict["Pfcsttiime"] = hm
    return pdict

    
# request로 Pfcstdate와 Pfcsttiime 받아오면 됨
# 또는 현재시각을 잘 손봐서 넣으면 됨
# 전체지역 1시간
def get_we_data_now(request):
    ymd = based_ymdgetter()
    pdict = ymd_timegetter()
    Pfcstdate = pdict["Pfcstdate"]
    Pfcsttiime = pdict["Pfcsttiime"]
    test = WeatherData.objects.using('redshift').filter(basedate=ymd).filter(fcstdate=Pfcstdate).filter(fcsttiime=Pfcsttiime)

# nx와 ny 값 받아서 Pnx Pny로
# 세부 지역 - 1군데 예측된값 전부 즉 제일 최신 basedate
def get_we_data_xy(request):
    ymd = based_ymdgetter()
    Pnx = "38"
    Pny = "123"
    test = WeatherData.objects.using('redshift').filter(basedate=ymd).filter(nx=Pnx).filter(ny=Pny)


def we_data_setting(dataList):    
    new_dataList = []
    checkerDict = {}
    newdata = {}
    for data in dataList:
        if checkerDict :
            if we_validation(data, checkerDict) : 
                newdata[data['category']] = data['fcstValue']
            else :
                new_dataList.append(newdata)
                checkerDict['fcstDate'] = data['fcstDate']
                checkerDict['fcstTime'] = data['fcstTime']
                checkerDict['nx'] = data['nx']
                checkerDict['ny'] = data['ny']
                newdata['fcstDate'] = data['fcstDate']
                newdata['fcstTime'] = data['fcstTime']
                newdata['nx'] = data['nx']
                newdata['ny'] = data['ny']
        else :
            checkerDict['fcstDate'] = data['fcstDate']
            checkerDict['fcstTime'] = data['fcstTime']
            checkerDict['nx'] = data['nx']
            checkerDict['ny'] = data['ny']
            newdata['fcstDate'] = data['fcstDate']
            newdata['fcstTime'] = data['fcstTime']
            newdata['nx'] = data['nx']
            newdata['ny'] = data['ny']
    return new_dataList

def we_validation(data, sample):
    if data['fcstDate'] == sample['fcstDate'] and data['fcstTime'] == sample['fcstTime'] and data['ny'] == data['ny'] and data['nx'] == data['nx'] :
        print(data['fcstDate'] == sample['fcstDate'], data['fcstTime'] == sample['fcstTime'], data['ny'] == data['ny'], data['nx'] == data['nx'])
        return True
    return False
    
    

# { 
#     "date" : "",
#     "time" : "",
#     "values" : {
#         "TMP" : 
#         }
#     },
#     'nx' : '',
#     'ny' : '',
# }