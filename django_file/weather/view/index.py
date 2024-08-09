from django.shortcuts import render
from datetime import datetime
from weather.models import musinsaData
import json

def get_weather_image(target_obs):
    obs_dict = {'강수량': 'precip', '기온': 'temp', '바람': 'wind'}
    obs_str = obs_dict.get(target_obs)
    time_now = datetime.now()
    year = time_now.strftime("%Y")
    month = time_now.strftime("%m")
    date = time_now.strftime("%d")
    hour = time_now.strftime('%H')
    
    if target_obs == '강수량':
        if int(hour) < 3:
            hour = '00'
        elif int(hour) < 6:
            hour = '03'
        elif int(hour) < 9:
            hour = '06'
        elif int(hour) < 12:
            hour = '09'
        elif int(hour) < 15:
            hour = '12'
        elif int(hour) < 18:
            hour = '15'
        elif int(hour) < 21:
            hour = '18'
        else:
            hour = '21'
            
    BASE_URL = f'https://www.weatheri.co.kr/images/super/{obs_str}{year}{month}{date}{hour}00.jpg'
    
    weather_dict = {'강수량': 'precip', '기온': 'forecast11', '바람': 'wind'}
    weather_str = weather_dict.get(target_obs)
    WEATHER_SITE = f'https://www.weatheri.co.kr/forecast/{weather_str}.php'
    return BASE_URL, WEATHER_SITE

def weather_view(request):
    temp_img, temp_link = get_weather_image('기온')
    precip_img, precip_link = get_weather_image('강수량')
    wind_img, wind_link = get_weather_image('바람')

    selected_gender = request.GET.get('gender')
    musinsaLists = musinsaData.objects.using('redshift').filter(gender = selected_gender)
    musinsaLists.order_by('rank')

    context = {
        'im': precip_img,
        'im2': precip_link,
        'im3': temp_img,
        'im4': temp_link,
        'im5': wind_img,
        'im6': wind_link,
        'musinsa_lists': musinsaLists,
    }

    return render(request, 'index.html', context)