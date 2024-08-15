from django.shortcuts import render
from datetime import datetime, timedelta
from weather.models import WeatherData, WeatherStn
from weather.view import nxny, save_location
from django.http import JsonResponse


# 좌표로 기상 검색
# we_data_setting(get_we_data_xy(y좌표, x좌표)) => json형태 결과값 출력 해당결과를 페이지로 보내주면됨

# 현재 시간으로 기상 검색
# we_data_setting(get_we_data_now()) => json으로 전체지역의 기상 현황 해당결과를 페이지로 보내주면됨


def we_data_usenow(request):
    wedata = get_we_data_now()
    context = { 'we_dataList' : we_data_setting(wedata)}
    print(context)
    return render(request, 'wedatatest.html', context)

def we_data_usetime(request):
    wedata = get_we_data_time()
    context = { 'we_dataList' : we_data_setting(wedata)}
    return JsonResponse(context)

def we_data_usexy(request):
    param = request.GET.get('param')
    if param == '2' :
        latitude = request.session.get('selectedLatitude', 'No latitude in session')
        longitude = request.session.get('selectedLongitude', 'No longitude in session')
        head = request.session.get('selectedDistrict')
        if head is None :
            head = "선택 지역의 날씨"
        else : 
            head = head+"의 날씨"
        
    elif param == '1' :
        latitude = request.session.get('latitude', 'No latitude in session')
        longitude = request.session.get('longitude', 'No longitude in session')
        head = "현 위치의 날씨"
    else :
        wedata = get_we_data_xy(60, 127)
        context = { 'head' : "서울의 날씨", 'we_dataList' : we_data_setting(wedata)}
        return JsonResponse(context)
        
    posXY = nxnySetting(str(longitude), str(latitude))
    print(posXY['nx'], posXY['ny'])
    wedata = get_we_data_xy(posXY['nx'], posXY['ny'])
    context = { 'head' : head ,'we_dataList' : we_data_setting(wedata)}
    return JsonResponse(context)

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
    result = WeatherData.objects.using('redshift').filter(
        basedate=ymd, 
        fcstdate=Pfcstdate, 
        fcsttime=Pfcsttime
    ).order_by('nx','ny').values()
    return result

def get_we_data_time(time=None):
    ymd = based_ymdgetter()
    pdict = ymd_timegetter()
    if time is None :
        Pfcstdate = pdict["Pfcstdate"]
    else :
        Pfcstdate = time
    Pfcsttime = pdict["Pfcsttime"]
    result = WeatherData.objects.using('redshift').filter(
        basedate=ymd, 
        fcstdate=Pfcstdate, 
        fcsttime=Pfcsttime
    ).order_by('nx','ny').values()
    return result
# y와 x 값 받아서 nx ny로
# 세부 지역 - 1군데 예측된값 전부 즉 제일 최신 basedate
def get_we_data_xy(x, y, time=None):
    ymd = based_ymdgetter()
    pdict = ymd_timegetter()
    if time is None :
        Pfcstdate = pdict["Pfcstdate"]
    else :
        Pfcstdate = time
    result = WeatherData.objects.using('redshift').filter(
        basedate=ymd,
        nx=x,
        ny=y,
        fcstdate=Pfcstdate, 
    ).order_by('nx','ny','fcstdate','fcsttime').values()
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
                new_dataList.append(newdata)
                newdata = {}
                checkerDict['fcstdate'] = data['fcstdate']
                checkerDict['fcsttime'] = data['fcsttime']
                checkerDict['nx'] = data['nx']
                checkerDict['ny'] = data['ny']
                newdata['fcstdate'] = data['fcstdate']
                newdata['fcsttime'] = data['fcsttime']
                newdata['nx'] = data['nx']
                newdata['ny'] = data['ny']
                newdata[data['weather_code']] = data['fcstvalue']
        else :
            checkerDict['fcstdate'] = data['fcstdate']
            checkerDict['fcsttime'] = data['fcsttime']
            checkerDict['nx'] = data['nx']
            checkerDict['ny'] = data['ny']
            newdata['fcstdate'] = data['fcstdate']
            newdata['fcsttime'] = data['fcsttime']
            newdata['nx'] = data['nx']
            newdata['ny'] = data['ny']
            newdata[data['weather_code']] = data['fcstvalue']
    if newdata:
        new_dataList.append(newdata)
    modified_data = list(map(lambda obj: {**obj, 'imgurl': weather_imgurl(obj)}, new_dataList))
    # print(new_dataList)
    return modified_data

def we_validation(data, sample):
    if data['fcstdate'] == sample['fcstdate'] and data['fcsttime'] == sample['fcsttime'] and data['ny'] == sample['ny'] and data['nx'] == sample['nx'] :
        # print(data['fcstdate'] == sample['fcstdate'], data['fcsttime'] == sample['fcsttime'], data['ny'] == sample['ny'], data['nx'] == sample['nx'])
        return True
    return False

def weather_imgurl(param):
    path = "img/"
    if param :
        imgurl = ""
        if param['PTY'] == "0":
            imgurl = path+"sky"+param['SKY']+".png"
        else :
            imgurl = path+"pty"+param['PTY']+".png"
        return imgurl
    return


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
    value = WeatherStn.getnxny(lon[:5],lat[:4])[0]
    result = {
        'nx' : value.nx,
        'ny' : value.ny
    }
    return result


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