from django.shortcuts import render
from datetime import datetime, timedelta
from weather.models import WeatherData
from weather.view import nxny
from django.http import JsonResponse

def we_data_test(request):
    # test = WeatherData.objects.using('redshift').all()
    test = testdataset() # [{'baseDate': '20240729', 'baseTime': '0500', 'category': 'TMP', 'fcstDate': '20240729', 'fcstTime': '0600', 'fcstValue': '26', 'nx': '34', 'ny': '126'}, {'baseDate': '20240729', 'baseTime': '0500', 'category': 'UUU', 'fcstDate': '20240729', 'fcstTime': '0600', 'fcstValue': '5.5', 'nx': '34', 'ny': '126'}, {'baseDate': '20240729', 'baseTime': '0500', 'category': 'VVV', 'fcstDate': '20240729', 'fcstTime': '0600', 'fcstValue': '6.6', 'nx': '34', 'ny': '126'}, {'baseDate': '20240729', 'baseTime': '0500', 'category': 'VEC', 'fcstDate': '20240729', 'fcstTime': '0600', 'fcstValue': '220', 'nx': '34', 'ny': '126'}, {'baseDate': '20240729', 'baseTime': '0500', 'category': 'WSD', 'fcstDate': '20240729', 'fcstTime': '0600', 'fcstValue': '8.6', 'nx': '34', 'ny': '126'}, {'baseDate': '20240729', 'baseTime': '0500', 'category': 'SKY', 'fcstDate': '20240729', 'fcstTime': '0600', 'fcstValue': '3', 'nx': '34', 'ny': '126'}, {'baseDate': '20240729', 'baseTime': '0500', 'category': 'PTY', 'fcstDate': '20240729', 'fcstTime': '0600', 'fcstValue': '0', 'nx': '34', 'ny': '126'}, {'baseDate': '20240729', 'baseTime': '0500', 'category': 'POP', 'fcstDate': '20240729', 'fcstTime': '0600', 'fcstValue': '20', 'nx': '34', 'ny': '126'}, {'baseDate': '20240729', 'baseTime': '0500', 'category': 'WAV', 'fcstDate': '20240729', 'fcstTime': '0600', 'fcstValue': '2', 'nx': '34', 'ny': '126'}, {'baseDate': '20240729', 'baseTime': '0500', 'category': 'PCP', 'fcstDate': '20240729', 'fcstTime': '0600', 'fcstValue': '강수없음', 'nx': '34', 'ny': '126'}]
    context = {'we_dataList' : we_data_setting(test)}
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
                nxnypos = nxnySetting(lon=int(data['ny']), lat=int(data['nx']))
                print(new_dataList)
                newdata = {}
                checkerDict['fcstDate'] = data['fcstDate']
                checkerDict['fcstTime'] = data['fcstTime']
                checkerDict['nx'] = data['nx']
                checkerDict['ny'] = data['ny']
                newdata['fcstDate'] = data['fcstDate']
                newdata['fcstTime'] = data['fcstTime']
                newdata['nx'] = nxnypos['nx']
                newdata['ny'] = nxnypos['ny']
        else :
            nxnypos = nxnySetting(lon=int(data['ny']), lat=int(data['nx']))
            checkerDict['fcstDate'] = data['fcstDate']
            checkerDict['fcstTime'] = data['fcstTime']
            checkerDict['nx'] = data['nx']
            checkerDict['ny'] = data['ny']
            newdata['fcstDate'] = data['fcstDate']
            newdata['fcstTime'] = data['fcstTime']
            newdata['nx'] = nxnypos['nx']
            newdata['ny'] = nxnypos['ny']
    new_dataList.append(newdata)
    print(new_dataList)
    return new_dataList

def we_validation(data, sample):
    if data['fcstDate'] == sample['fcstDate'] and data['fcstTime'] == sample['fcstTime'] and data['ny'] == data['ny'] and data['nx'] == data['nx'] :
        print(data['fcstDate'] == sample['fcstDate'], data['fcstTime'] == sample['fcstTime'], data['ny'] == data['ny'], data['nx'] == data['nx'])
        return True
    return False
    

def testdataset():
    json_output = [
    {"baseDate": "20240724", "baseTime": "500", "category": "TMP", "fcstDate": "20240724", "fcstTime": "600", "fcstValue": "25", "nx": "33", "ny": "126"},
    {"baseDate": "20240724", "baseTime": "500", "category": "UUU", "fcstDate": "20240724", "fcstTime": "600", "fcstValue": "0.8", "nx": "33", "ny": "126"},
    {"baseDate": "20240724", "baseTime": "500", "category": "VVV", "fcstDate": "20240724", "fcstTime": "600", "fcstValue": "4.6", "nx": "33", "ny": "126"},
    {"baseDate": "20240724", "baseTime": "500", "category": "VEC", "fcstDate": "20240724", "fcstTime": "600", "fcstValue": "190", "nx": "33", "ny": "126"},
    {"baseDate": "20240724", "baseTime": "500", "category": "WSD", "fcstDate": "20240724", "fcstTime": "600", "fcstValue": "4.7", "nx": "33", "ny": "126"},
    {"baseDate": "20240724", "baseTime": "500", "category": "SKY", "fcstDate": "20240724", "fcstTime": "600", "fcstValue": "1", "nx": "33", "ny": "126"},
    {"baseDate": "20240724", "baseTime": "500", "category": "PTY", "fcstDate": "20240724", "fcstTime": "600", "fcstValue": "0", "nx": "33", "ny": "126"},
    {"baseDate": "20240724", "baseTime": "500", "category": "POP", "fcstDate": "20240724", "fcstTime": "600", "fcstValue": "0", "nx": "33", "ny": "126"},
    {"baseDate": "20240724", "baseTime": "500", "category": "WAV", "fcstDate": "20240724", "fcstTime": "600", "fcstValue": "1", "nx": "33", "ny": "126"},
    {"baseDate": "20240724", "baseTime": "500", "category": "PCP", "fcstDate": "20240724", "fcstTime": "600", "fcstValue": "강수없음", "nx": "33", "ny": "126"},
    {"baseDate": "20240724", "baseTime": "500", "category": "TMP", "fcstDate": "20240724", "fcstTime": "600", "fcstValue": "25", "nx": "34", "ny": "125"},
    {"baseDate": "20240724", "baseTime": "500", "category": "UUU", "fcstDate": "20240724", "fcstTime": "600", "fcstValue": "1", "nx": "34", "ny": "125"},
    {"baseDate": "20240724", "baseTime": "500", "category": "VVV", "fcstDate": "20240724", "fcstTime": "600", "fcstValue": "4.8", "nx": "34", "ny": "125"},
    {"baseDate": "20240724", "baseTime": "500", "category": "VEC", "fcstDate": "20240724", "fcstTime": "600", "fcstValue": "192", "nx": "34", "ny": "125"},
    {"baseDate": "20240724", "baseTime": "500", "category": "WSD", "fcstDate": "20240724", "fcstTime": "600", "fcstValue": "4.9", "nx": "34", "ny": "125"},
    {"baseDate": "20240724", "baseTime": "500", "category": "SKY", "fcstDate": "20240724", "fcstTime": "600", "fcstValue": "1", "nx": "34", "ny": "125"},
    {"baseDate": "20240724", "baseTime": "500", "category": "PTY", "fcstDate": "20240724", "fcstTime": "600", "fcstValue": "0", "nx": "34", "ny": "125"},
    {"baseDate": "20240724", "baseTime": "500", "category": "POP", "fcstDate": "20240724", "fcstTime": "600", "fcstValue": "0", "nx": "34", "ny": "125"},
    {"baseDate": "20240724", "baseTime": "500", "category": "WAV", "fcstDate": "20240724", "fcstTime": "600", "fcstValue": "1", "nx": "34", "ny": "125"},
    {"baseDate": "20240724", "baseTime": "500", "category": "PCP", "fcstDate": "20240724", "fcstTime": "600", "fcstValue": "강수없음", "nx": "34", "ny": "125"}]

    # 출력 결과 확인
    print(json_output)
    return json_output


def nxnySetting(lon, lat):
    print(lon, lat)
    lon, lat, x, y = nxny.map_conv(lon, lat, 0.0, 0.0, 0)
    result = {'lon':str(lon), 'lat':str(lat), 'nx':str(x),'ny':str(y)}
    print(result)
    
    return result

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



def get_weather_data(request):
    # 세션에서 위도와 경도 정보를 가져옴
    latitude = request.session.get('latitude')
    longitude = request.session.get('longitude')

    if latitude is not None and longitude is not None:
        # weather_data 테이블에서 nx와 ny가 세션의 위도와 경도와 일치하는 레코드 조회
        weather_data_records = WeatherData.objects.filter(nx=latitude, ny=longitude)
        data = [
            {
                'basedate': record.basedate,
                'basetime': record.basetime,
                'weather_code': record.weather_code,
                'fcstdate': record.fcstdate,
                'fcsttime': record.fcsttime,
                'fcstvalue': record.fcstvalue,
                'nx': record.nx,
                'ny': record.ny
            }
            for record in weather_data_records
        ]
        return JsonResponse({'status': 'success', 'data': data})
    else:
        return JsonResponse({'status': 'error', 'message': 'No location data in session'}, status=400)