import pandas as pd
from datetime import datetime, timedelta
import pytz
from weather.models import WeatherData
from django.http import HttpResponse
from django.core.cache import cache
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.db.models import Max


seoul_tz = pytz.timezone('Asia/Seoul')
current_hour = datetime.now(seoul_tz).hour

LOCATIONS = [
    {'name': '서울', 'nx': 60, 'ny': 127, 'zone': 'z1'},
    {'name': '백령도', 'nx': 21, 'ny': 135, 'zone': 'z2'},
    {'name': '수원', 'nx': 60, 'ny': 121, 'zone': 'z3'},  # 수원도 서울과 같은 nx, ny를 사용
    {'name': '춘천', 'nx': 73, 'ny': 134, 'zone': 'z4'},
    {'name': '강릉', 'nx': 92, 'ny': 131, 'zone': 'z5'},
    {'name': '청주', 'nx': 69, 'ny': 106, 'zone': 'z6'},
    {'name': '대전', 'nx': 67, 'ny': 100, 'zone': 'z7'},
    {'name': '전주', 'nx': 63, 'ny': 89, 'zone': 'z8'},
    {'name': '광주', 'nx': 58, 'ny': 74, 'zone': 'z9'},
    {'name': '목포', 'nx': 50, 'ny': 67, 'zone': 'z10'},
    {'name': '여수', 'nx': 73, 'ny': 66, 'zone': 'z11'},
    {'name': '울릉도', 'nx': 127, 'ny': 127, 'zone': 'z12'},
    {'name': '안동', 'nx': 91, 'ny': 106, 'zone': 'z13'},
    {'name': '대구', 'nx': 89, 'ny': 90, 'zone': 'z14'},
    {'name': '울산', 'nx': 102, 'ny': 84, 'zone': 'z15'},
    {'name': '부산', 'nx': 98, 'ny': 76, 'zone': 'z16'},
    {'name': '제주', 'nx': 52, 'ny': 38, 'zone': 'z17'},
]

def setting(row):
    value = int(row['fcstvalue'])
    time = int(row['fcsttime'])
    hour = time // 100
    night = hour < 6 or hour > 18

    return value,night
    
def classify_weather(nx, ny, fcstdate):
    # 가장 최근인 basedate 가져오기
    latest_basedate = WeatherData.objects.filter(
        fcstdate=fcstdate,
        nx=nx,
        ny=ny
    ).aggregate(Max('basedate'))['basedate__max']
    
    print(latest_basedate)

    # 최신 basedate로 데이터 필터링
    current_hour_str = f"{current_hour:02}00" #현재 시간이 자꾸,,,어떤건 0700 어떤건 700,,
    weather_data = WeatherData.objects.filter(
        basedate=latest_basedate,
        fcstdate=fcstdate,
        fcsttime=current_hour_str,
        nx=nx,
        ny=ny
    ).order_by('nx','ny','basedate', 'weather_code').values()
    
    if not weather_data:
        print("No weather data found for the given parameters.")
        print(current_hour_str)
        print(fcstdate)
        print(nx)
        print(ny)
        return None
    
    df = pd.DataFrame(weather_data)
    print(df.head())  # 데이터 확인

    # 'fcsttime'이 현재 시각의 '시'와 일치하는 데이터 필터링
    #current_hour_str = f"{current_hour:02}00"
    current_data = df[df['fcsttime'] == current_hour_str]
    tmp = None
    for _, row in current_data.iterrows():
        if row['weather_code'] == 'TMP':
            tmp = row['fcstvalue']
            break  # TMP 값을 찾으면 중단
            
    
    # 우선순위 기반으로 가장 중요한 상태 결정
    
    priority_order = [ 'PTY','SKY']
    # 상태 번호와 설명을 저장할 리스트
    condition = []

    for code in priority_order:
        # 각 코드에 대한 우선순위로 상태 평가
        for _, row in current_data.iterrows():
            if row['weather_code'] == code :
                value,night = setting(row)
            else : continue
            condition = []
            # 하늘 상태(SKY)
            if code == 'SKY':
                if value == 1:  
                    condition = [1, "맑음"]
                    if night:
                        condition = [2, "밤에 맑음"]
                elif value == 3:
                    condition = [3, "구름 많음"]
                    if night:
                        condition = [4, "밤에 구름 많음"]
                elif value == 4:  # 흐림
                    condition = [5, "흐림"]
                    if night:
                        condition = [6, "밤에 흐림"]

            # 강수 형태(PTY)
            if code == 'PTY':
                if value == 0:
                    code = "SKY"
                    continue
                elif value == 1:
                    condition = [10, "흐리고 비"]
                elif value == 2:
                    condition = [21, "진눈깨비"]
                elif value == 3:
                    condition = [12, "눈"]
                elif value == 4:
                    condition = [9, "소나기"]
                    if night:
                        condition = [38, "밤에 소나기"]

            # 첫 번째로 발견된 가장 높은 우선순위의 상태에서 탈출
            if condition:
                condition.append(tmp)
                break
        if condition:
            condition.append(tmp)
            break
    condition.append(tmp)
    print(condition)
    return condition



def test_weather_view(request):
    today = datetime.now(seoul_tz).date()
    todayformat = today.strftime("%Y%m%d")
    
    weather_conditions = classify_weather(nx=8, ny=115, fcstdate=todayformat)
    
    context = {
        'weather_conditions': weather_conditions
    }
    
    if weather_conditions:
        return HttpResponse(f"Weather Condition: {weather_conditions[1]}, Code: {weather_conditions[0]}, TMP: {weather_conditions[2]}")
    else:
        return HttpResponse("No weather data available")


@require_GET #null값이 들어있을 때, 새로고침하면 캐시 비움
def weather_api(request):
    now = datetime.now(seoul_tz)
    current_hour = now.hour
    fcstdate = now.strftime("%Y%m%d") #얘도 나중에 3일치로 for문 돌릴 예정
    #캐시 키 생성
    cache_key = f'weather_data_{fcstdate}_{current_hour}'
    
    # 캐시에서 데이터 확인
    cached_data = cache.get(cache_key)
    if cached_data is not None:
        # 캐시된 데이터 중 하나라도 condition_code가 None이면 오류를 반환
        for zone, data in cached_data.items():
            if data["condition_code"] is None:
                #캐시비우기
                cache.delete(cache_key)
                return JsonResponse({'error': '데이터 오류'}, status=500)
        return JsonResponse(cached_data)
    
    # 캐시에 데이터가 없으면 새로 생성
    all_weather_data = {}
    for location in LOCATIONS:
        condition = classify_weather(location['nx'], location['ny'], fcstdate)
        all_weather_data[location['zone']] = {
            'zone': location['zone'],
            'condition_code': condition[0] if condition else None,
            'weather_condition': condition[1] if condition else None,
            'tmp': condition[2] if condition else None,
        }
    # 이전 시간의 캐시 삭제
    if current_hour == 0:
        # 자정을 넘어갈 경우 fcstdate도 전날로 설정
        previous_day = now - timedelta(days=1)
        previous_fcstdate = previous_day.strftime("%Y%m%d")
    else:
        previous_fcstdate = fcstdate

    previous_hour = (now - timedelta(hours=1)).hour
    previous_cache_key = f'weather_data_{previous_fcstdate}_{previous_hour}'
    cache.delete(previous_cache_key)

    # 데이터를 1시간 동안 캐시에 저장
    cache.set(cache_key, all_weather_data, 60 * 60)  # 60분 * 60초 = 1시간
    
    return JsonResponse(all_weather_data)

