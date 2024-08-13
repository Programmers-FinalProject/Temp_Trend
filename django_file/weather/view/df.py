import pandas as pd
from datetime import datetime
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
    {'name': '서울', 'nx': 43, 'ny': 114, 'zone': 'z1'},
    {'name': '백령도', 'nx': 8, 'ny': 115, 'zone': 'z2'},
    {'name': '수원', 'nx': 43, 'ny': 114, 'zone': 'z3'},  # 수원도 서울과 같은 nx, ny를 사용
    {'name': '춘천', 'nx': 60, 'ny': 114, 'zone': 'z4'},
    {'name': '강릉', 'nx': 78, 'ny': 115, 'zone': 'z5'},
    {'name': '청주', 'nx': 61, 'ny': 93, 'zone': 'z6'},
    {'name': '대전', 'nx': 61, 'ny': 93, 'zone': 'z7'},
    {'name': '전주', 'nx': 61, 'ny': 71, 'zone': 'z8'},
    {'name': '광주', 'nx': 43, 'ny': 71, 'zone': 'z9'},
    {'name': '목포', 'nx': 43, 'ny': 49, 'zone': 'z10'},
    {'name': '여수', 'nx': 61, 'ny': 49, 'zone': 'z11'},
    {'name': '울릉도', 'nx': 112, 'ny': 116, 'zone': 'z12'},
    {'name': '안동', 'nx': 78, 'ny': 93, 'zone': 'z13'},
    {'name': '대구', 'nx': 79, 'ny': 71, 'zone': 'z14'},
    {'name': '울산', 'nx': 97, 'ny': 72, 'zone': 'z15'},
    {'name': '부산', 'nx': 97, 'ny': 72, 'zone': 'z16'},
    {'name': '제주', 'nx': 43, 'ny': 27, 'zone': 'z17'},
]

def classify_weather(nx, ny, fcstdate):
        # 가장 최근의 basedate 가져오기
    latest_basedate = WeatherData.objects.filter(
        fcstdate=fcstdate,
        nx=nx,
        ny=ny
    ).aggregate(Max('basedate'))['basedate__max']
    
    print(latest_basedate)

    # 최신 basedate로 데이터 필터링
    current_hour_str = f"{current_hour:02}00"
    weather_data = WeatherData.objects.filter(
        basedate=latest_basedate,
        fcstdate=fcstdate,
        fcsttime=current_hour_str,
        nx=nx,
        ny=ny
    ).order_by('nx','ny','basedate', 'weather_code').values()
    
    df = pd.DataFrame(weather_data)
    print(df.head())  # 데이터 확인

    # 'fcsttime'이 현재 시각의 '시'와 일치하는 데이터 필터링
    # current_hour_str = f"{current_hour:02}00"
    current_data = df[df['fcsttime'] == current_hour_str]
    print("!!!!!!!!!!!!!!!!!!!!!",nx,ny, current_data)
    
    # 우선순위 기반으로 가장 중요한 상태 결정
    priority_order = [
        'TMP', 'PTY', 'TMP', 'WSD', 'SKY', 'VVV', 'REH', 'WAV'
    ]
    condition = None
    tmp = 0
    for code in priority_order:
        # 각 코드에 대한 우선순위로 상태 평가
        for _, row in current_data.iterrows():
            if row['weather_code'] == 'TMP':
                tmp = row['fcstvalue']
            if row['weather_code'] != code:
                continue
            
            value = float(row['fcstvalue'])
            time = int(row['fcsttime'])
            hour = time // 100
            night = hour < 6 or hour > 18

            # 상태 번호와 설명을 저장할 리스트
            condition = None

            # 하늘 상태(SKY)
            if code == 'SKY':
                if value == 1:  
                    condition = [1, "맑음"]
                    if night:
                        condition = [13, "밤에 맑음"]
                elif value == 3:
                    condition = [2, "구름 많음"]
                    if night:
                        condition = [30, "밤에 구름 많음"]
                elif value == 4:  # 흐림
                    condition = [4, "흐림"]
                    if night:
                        condition = [15, "밤에 흐림"]

            # 강수 형태(PTY)
            elif code == 'PTY':
                if value == 0:
                    condition = [1, "맑음"]  # 맑음 (하늘 상태로 따로 처리)
                elif value == 1:
                    condition = [5, "흐리고 비"]
                elif value == 2:
                    condition = [25, "진눈깨비"]
                elif value == 3:
                    condition = [21, "흐리고 눈"]
                elif value == 4:
                    condition = [6, "소나기"]
                    if night:
                        condition = [33, "밤에 소나기"]
                elif value == 5:
                    condition = [26, "빗방울"]
                elif value == 6:
                    condition = [27, "빗방울눈날림"]
                elif value == 7:
                    condition = [28, "눈날림"]

            # 기온(TMP)
            elif code == 'TMP':
                if value > 35:
                    condition = [41, "매우 더운 날"]
                elif value > 30:
                    condition = [8, "더운 날"]
                    if night:
                        condition = [39, "더운 밤"]
                elif value < 0:
                    condition = [9, "추운 날"]
                    if 5 <= hour <= 8:
                        condition = [38, "차가운 아침"]
                    if night:
                        condition = [40, "추운 밤"]
                elif value < -10:
                    condition = [42, "매우 추운 날"]

            # 습도(REH)
            elif code == 'REH':
                if value > 90:
                    condition = [16, "습도가 높아 안개"]
                elif value > 80:
                    if row.get('SKY') == 3:
                        condition = [29, "구름 많고 습도 높음"]
                    elif row.get('SKY') == 4:
                        condition = [31, "흐리고 습도 높음"]

            # 습도와 기온 조합
            if code == 'REH' and value > 70 and row.get('TMP', 0) > 30:
                condition = [32, "고온 다습"]
            elif code == 'REH' and value < 40 and row.get('TMP', 0) < 10:
                condition = [35, "저온 건조"]

            # 풍속(WSD)
            elif code == 'WSD':
                if value > 8:
                    if row.get('SKY', 0) == 3:
                        condition = [11, "구름 많고 바람이 강한 날"]
                    elif row.get('SKY', 0) == 4:
                        condition = [12, "흐리고 바람이 강한 날"]
                    else:
                        condition = [10, "강풍"]
                elif value > 10:
                    condition = [34, "매우 강풍"]

            # 풍향(VEC), 바람 동서성분(VVV)
            elif code == 'VVV':
                if value < 0:
                    condition = [18, "서풍"]
                elif value > 0:
                    condition = [19, "동풍"]

            # 파고(WAV)
            elif code == 'WAV':
                if value > 2:
                    condition = [20, "높은 파도"]

            # 특정 날씨 조합
            if code == 'PTY' and value == 1 and row.get('WSD', 0) > 8:
                condition = [22, "비와 강풍"]
            elif code == 'PTY' and value == 3 and row.get('WSD', 0) > 8:
                condition = [23, "눈과 강풍"]

            # 시간 및 특정 조건에 따른 추가 상태
            if condition is None:
                if night:
                    if code == 'SKY' and value == 1:
                        condition = [13, "밤에 맑음"]
                    elif code == 'SKY' and value == 3:
                        condition = [30, "밤에 구름 많음"]
                if 5 <= hour <= 8 and code == 'TMP' and value < 0:
                    condition = [38, "차가운 아침"]
                elif 18 <= hour <= 20 and code == 'SKY' and value == 1:
                    condition = [41, "해질녘 맑음"]
                elif 4 <= hour <= 6 and code == 'SKY' and value == 1:
                    condition = [42, "해뜰 때 맑음"]

            # 추가 조건 정의
            if code == 'SKY' and value == 3 and row.get('REH', 0) > 85:
                condition = [3, "구름 조금"]
            if code == 'PTY' and value == 4 and row.get('WSD', 0) > 10:
                condition = [7, "폭우와 강풍"]
            if code == 'SKY' and value == 3 and row.get('REH', 0) > 95:
                condition = [14, "밤에 안개"]
            if code == 'SKY' and value == 4 and row.get('REH', 0) > 95:
                condition = [17, "밤에 흐리고 안개"]
            if code == 'VVV' and row.get('WSD', 0) > 15:
                condition = [24, "강한 바람"]
            if code == 'SKY' and value == 3 and row.get('TMP', 0) < 15:
                condition = [36, "구름 많고 추운 날"]
            if code == 'SKY' and value == 4 and row.get('TMP', 0) < 15:
                condition = [37, "흐리고 추운 날"]

            # 첫 번째로 발견된 가장 높은 우선순위의 상태에서 탈출
            if condition:
                break
        if condition:
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


@require_GET
def weather_api(request):
    fcstdate = datetime.now(seoul_tz).strftime("%Y%m%d") #얘도 나중에 3일치로 for문 돌릴 예정
    #캐시 키 생성
    cache_key = f'weather_data_{fcstdate}_{current_hour}'
    
    # 캐시에서 데이터 확인
    cached_data = cache.get(cache_key)
    if cached_data is not None:
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
    
    # 데이터를 1시간 동안 캐시에 저장
    cache.set(cache_key, all_weather_data, 60 * 60)  # 60분 * 60초 = 1시간
    
    return JsonResponse(all_weather_data)

