from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json
from weather.models import LocationRecord
import os
import requests
from dotenv import load_dotenv
from django.shortcuts import render


load_dotenv()


@csrf_exempt
@require_POST
def save_location(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        location_type = data.get('location_type')

        # 세션 키 가져오기
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key

        # 세션에 위치 정보 저장
        request.session['latitude'] = latitude
        request.session['longitude'] = longitude
        request.session['location_type'] = location_type

        # 데이터베이스에 위치 정보 저장 (옵션)
        '''
        location_record = LocationRecord(
            latitude=latitude,
            longitude=longitude,
            location_type=location_type,
            session=session_key
        )
        location_record.save()
        '''

        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)



def get_location_name_from_kakao(latitude, longitude):
    api_key = os.getenv('KAKAO_API_KEY')  # 카카오 API 키
    url = f"https://dapi.kakao.com/v2/local/geo/coord2address.json?x={longitude}&y={latitude}"
    headers = {
        "Authorization": f"KakaoAK {api_key}"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        try:
            address = response.json()["documents"][0]["address"]["address_name"]
            return address
        except (IndexError, KeyError):
            return "No address found"
    else:
        return f"Error: {response.status_code}"

@csrf_exempt
def location_name(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        latitude = data.get('latitude')
        longitude = data.get('longitude')

        # 위치 이름 찾기
        address = get_location_name_from_kakao(latitude, longitude)
        request.session['address'] = address
        
        address = request.session.get('address', 'No address in session')
        return JsonResponse({'address': address})
    elif request.method == 'GET':
        latitude = request.GET.get('latitude')
        longitude = request.GET.get('longitude')

        if latitude is not None and longitude is not None:
            # 위치 이름 찾기
            address = get_location_name_from_kakao(latitude, longitude)

            return JsonResponse({'address': address})
        return JsonResponse({'status': 'error', 'message': 'Missing parameters'}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)


def session_data_api(request):
    address = request.session.get('address', 'No address in session')
    latitude = request.session.get('latitude', 'No latitude in session')
    longitude = request.session.get('longitude', 'No longitude in session')
    return JsonResponse({
        'address': address,
        'latitude': latitude,
        'longitude': longitude
    })