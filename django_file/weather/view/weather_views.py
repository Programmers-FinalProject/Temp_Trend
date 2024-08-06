from django.shortcuts import render
from datetime import datetime, timedelta
from weather.models import WeatherData
from weather.view import nxny
from django.http import JsonResponse


# 좌표로 기상 검색
# we_data_setting(get_we_data_xy(y좌표, x좌표)) => json형태 결과값 출력 해당결과를 페이지로 보내주면됨

# 현재 시간으로 기상 검색
# we_data_setting(get_we_data_now()) => json으로 전체지역의 기상 현황 해당결과를 페이지로 보내주면됨


def we_data_test(request):
    wedata = get_we_data_now()
    # test = testdataset() # [{'basedate': '20240729', 'basetime': '0500', 'weather_code': 'TMP', 'fcstdate': '20240729', 'fcsttime': '0600', 'fcstvalue': '26', 'nx': '34', 'ny': '126'}, {'basedate': '20240729', 'basetime': '0500', 'weather_code': 'UUU', 'fcstdate': '20240729', 'fcsttime': '0600', 'fcstvalue': '5.5', 'nx': '34', 'ny': '126'}, {'basedate': '20240729', 'basetime': '0500', 'weather_code': 'VVV', 'fcstdate': '20240729', 'fcsttime': '0600', 'fcstvalue': '6.6', 'nx': '34', 'ny': '126'}, {'basedate': '20240729', 'basetime': '0500', 'weather_code': 'VEC', 'fcstdate': '20240729', 'fcsttime': '0600', 'fcstvalue': '220', 'nx': '34', 'ny': '126'}, {'basedate': '20240729', 'basetime': '0500', 'weather_code': 'WSD', 'fcstdate': '20240729', 'fcsttime': '0600', 'fcstvalue': '8.6', 'nx': '34', 'ny': '126'}, {'basedate': '20240729', 'basetime': '0500', 'weather_code': 'SKY', 'fcstdate': '20240729', 'fcsttime': '0600', 'fcstvalue': '3', 'nx': '34', 'ny': '126'}, {'basedate': '20240729', 'basetime': '0500', 'weather_code': 'PTY', 'fcstdate': '20240729', 'fcsttime': '0600', 'fcstvalue': '0', 'nx': '34', 'ny': '126'}, {'basedate': '20240729', 'basetime': '0500', 'weather_code': 'POP', 'fcstdate': '20240729', 'fcsttime': '0600', 'fcstvalue': '20', 'nx': '34', 'ny': '126'}, {'basedate': '20240729', 'basetime': '0500', 'weather_code': 'WAV', 'fcstdate': '20240729', 'fcsttime': '0600', 'fcstvalue': '2', 'nx': '34', 'ny': '126'}, {'basedate': '20240729', 'basetime': '0500', 'weather_code': 'PCP', 'fcstdate': '20240729', 'fcsttime': '0600', 'fcstvalue': '강수없음', 'nx': '34', 'ny': '126'}]
    context = { 'we_dataList' : we_data_setting(wedata)}
    print(wedata)
    return render(request, 'wedatatest.html', context)

# 예보날짜 세팅
def based_ymdgetter():
    now = datetime.now()

    # 05시 30분 이전은 어제 예보 정보를 가지고 결과 보여줌
    hm = now.strftime("%H%M")
    ckhm = datetime.strptime("0530", "%H%M").strftime("%H%M")
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
    pdict["Pfcsttime"] = hm
    return pdict

    
# request로 Pfcstdate와 Pfcsttime 받아오면 됨
# 또는 현재시각을 잘 손봐서 넣으면 됨
# 전체지역 1시간
def get_we_data_now():
    ymd = based_ymdgetter()
    pdict = ymd_timegetter()
    Pfcstdate = pdict["Pfcstdate"]
    Pfcsttime = pdict["Pfcsttime"]
    print(ymd, Pfcstdate, Pfcsttime)
    result = WeatherData.objects.using('redshift').filter(
        basedate=ymd, 
        fcstdate=Pfcstdate, 
        fcsttime=Pfcsttime
    ).values()
    return result

# y와 x 값 받아서 nx ny로
# 세부 지역 - 1군데 예측된값 전부 즉 제일 최신 basedate
def get_we_data_xy(x, y):
    ymd = based_ymdgetter()
    nxnypos = nxnySetting(lon=int(y), lat=int(x))
    result = WeatherData.objects.using('redshift').filter(basedate=ymd).filter(nx=nxnypos['nx']).filter(ny=nxnypos['ny'])
    return result


def we_data_setting(dataList):    
    new_dataList = []
    checkerDict = {}
    newdata = {}
    for data in dataList:
        if checkerDict :
            if we_validation(data, checkerDict) : 
                newdata[data['weather_code']] = data['fcstvalue']
            else :
                newdata['imgurl'] = weather_imgurl(newdata)
                new_dataList.append(newdata)
                print(new_dataList)
                newdata = {}
                checkerDict['fcstdate'] = data['fcstdate']
                checkerDict['fcsttime'] = data['fcsttime']
                checkerDict['nx'] = data['nx']
                checkerDict['ny'] = data['ny']
                newdata['fcstdate'] = data['fcstdate']
                newdata['fcsttime'] = data['fcsttime']
                newdata['nx'] = data['nx']
                newdata['ny'] = data['ny']
        else :
            checkerDict['fcstdate'] = data['fcstdate']
            checkerDict['fcsttime'] = data['fcsttime']
            checkerDict['nx'] = data['nx']
            checkerDict['ny'] = data['ny']
            newdata['fcstdate'] = data['fcstdate']
            newdata['fcsttime'] = data['fcsttime']
            newdata['nx'] = data['nx']
            newdata['ny'] = data['ny']
    newdata['imgurl'] = weather_imgurl(newdata)
    new_dataList.append(newdata)
    print(new_dataList)
    return new_dataList

def we_validation(data, sample):
    if data['fcstdate'] == sample['fcstdate'] and data['fcsttime'] == sample['fcsttime'] and data['ny'] == data['ny'] and data['nx'] == data['nx'] :
        print(data['fcstdate'] == sample['fcstdate'], data['fcsttime'] == sample['fcsttime'], data['ny'] == data['ny'], data['nx'] == data['nx'])
        return True
    return False

def weather_imgurl(param):
    path = "img/"
    imgurl = ""
    if param['PTY'] == "0":
        imgurl = path+"sky"+param['SKY']+".png"
    else :
        imgurl = path+"pty"+param['PTY']+".png"
    return imgurl


def testdataset():
    json_output = [
    {"basedate": "20240724", "basetime": "500", "weather_code": "TMP", "fcstdate": "20240724", "fcsttime": "600", "fcstvalue": "25", "nx": "33", "ny": "126"},
    {"basedate": "20240724", "basetime": "500", "weather_code": "UUU", "fcstdate": "20240724", "fcsttime": "600", "fcstvalue": "0.8", "nx": "33", "ny": "126"},
    {"basedate": "20240724", "basetime": "500", "weather_code": "VVV", "fcstdate": "20240724", "fcsttime": "600", "fcstvalue": "4.6", "nx": "33", "ny": "126"},
    {"basedate": "20240724", "basetime": "500", "weather_code": "VEC", "fcstdate": "20240724", "fcsttime": "600", "fcstvalue": "190", "nx": "33", "ny": "126"},
    {"basedate": "20240724", "basetime": "500", "weather_code": "WSD", "fcstdate": "20240724", "fcsttime": "600", "fcstvalue": "4.7", "nx": "33", "ny": "126"},
    {"basedate": "20240724", "basetime": "500", "weather_code": "SKY", "fcstdate": "20240724", "fcsttime": "600", "fcstvalue": "1", "nx": "33", "ny": "126"},
    {"basedate": "20240724", "basetime": "500", "weather_code": "PTY", "fcstdate": "20240724", "fcsttime": "600", "fcstvalue": "0", "nx": "33", "ny": "126"},
    {"basedate": "20240724", "basetime": "500", "weather_code": "POP", "fcstdate": "20240724", "fcsttime": "600", "fcstvalue": "0", "nx": "33", "ny": "126"},
    {"basedate": "20240724", "basetime": "500", "weather_code": "WAV", "fcstdate": "20240724", "fcsttime": "600", "fcstvalue": "1", "nx": "33", "ny": "126"},
    {"basedate": "20240724", "basetime": "500", "weather_code": "PCP", "fcstdate": "20240724", "fcsttime": "600", "fcstvalue": "강수없음", "nx": "33", "ny": "126"},
    {"basedate": "20240724", "basetime": "500", "weather_code": "TMP", "fcstdate": "20240724", "fcsttime": "600", "fcstvalue": "25", "nx": "34", "ny": "125"},
    {"basedate": "20240724", "basetime": "500", "weather_code": "UUU", "fcstdate": "20240724", "fcsttime": "600", "fcstvalue": "1", "nx": "34", "ny": "125"},
    {"basedate": "20240724", "basetime": "500", "weather_code": "VVV", "fcstdate": "20240724", "fcsttime": "600", "fcstvalue": "4.8", "nx": "34", "ny": "125"},
    {"basedate": "20240724", "basetime": "500", "weather_code": "VEC", "fcstdate": "20240724", "fcsttime": "600", "fcstvalue": "192", "nx": "34", "ny": "125"},
    {"basedate": "20240724", "basetime": "500", "weather_code": "WSD", "fcstdate": "20240724", "fcsttime": "600", "fcstvalue": "4.9", "nx": "34", "ny": "125"},
    {"basedate": "20240724", "basetime": "500", "weather_code": "SKY", "fcstdate": "20240724", "fcsttime": "600", "fcstvalue": "1", "nx": "34", "ny": "125"},
    {"basedate": "20240724", "basetime": "500", "weather_code": "PTY", "fcstdate": "20240724", "fcsttime": "600", "fcstvalue": "0", "nx": "34", "ny": "125"},
    {"basedate": "20240724", "basetime": "500", "weather_code": "POP", "fcstdate": "20240724", "fcsttime": "600", "fcstvalue": "0", "nx": "34", "ny": "125"},
    {"basedate": "20240724", "basetime": "500", "weather_code": "WAV", "fcstdate": "20240724", "fcsttime": "600", "fcstvalue": "1", "nx": "34", "ny": "125"},
    {"basedate": "20240724", "basetime": "500", "weather_code": "PCP", "fcstdate": "20240724", "fcsttime": "600", "fcstvalue": "강수없음", "nx": "34", "ny": "125"}]

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
        weather_data_records = get_we_data_xy(latitude, longitude) # WeatherData.objects.filter(nx=latitude, ny=longitude)
        data = we_data_setting(weather_data_records)
        # data = [
        #     {
        #         'basedate': record.basedate,
        #         'basetime': record.basetime,
        #         'weather_code': record.weather_code,
        #         'fcstdate': record.fcstdate,
        #         'fcsttime': record.fcsttime,
        #         'fcstvalue': record.fcstvalue,
        #         'nx': record.nx,
        #         'ny': record.ny
        #     }
        #     for record in weather_data_records
        # ]
        return JsonResponse({'status': 'success', 'data': data})
    else:
        return JsonResponse({'status': 'error', 'message': 'No location data in session'}, status=400)