from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json
import numpy as np
import os
import requests
from dotenv import load_dotenv
import logging

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

        return JsonResponse({'status': 'success', 'message': 'location saved successfully.'})
    return JsonResponse({'status': 'fail', 'message': 'Invalid request method.'})

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




logger = logging.getLogger(__name__)

@csrf_exempt
@require_POST
def save_gender(request):
    logger.info("save_gender view called")
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            gender = data.get('gender')
            logger.info(f"Received gender: {gender}")
            
            if gender not in ['m', 'w', 'unisex']:
                logger.warning(f"Invalid gender value received: {gender}")
                return JsonResponse({'status': 'fail', 'message': 'Invalid gender value.'}, status=400)
            
            # 세션 키 가져오기
            session_key = request.session.session_key
            if not session_key:
                request.session.create()
                session_key = request.session.session_key

            # 세션에 성별 정보 저장
            request.session['selectedGender'] = gender
            logger.info(f"Gender saved in session: {gender}")

            # 데이터베이스에 성별 정보 저장 (옵션)
            '''
            gender_record = GenderRecord(
                gender=gender,
                session=session_key
            )
            gender_record.save()
            '''

            return JsonResponse({'status': 'success', 'message': 'Gender saved successfully.'})
        except json.JSONDecodeError:
            logger.error("Invalid JSON in request body")
            return JsonResponse({'status': 'fail', 'message': 'Invalid JSON in request body.'}, status=400)
        except Exception as e:
            logger.exception("Unexpected error in save_gender view")
            return JsonResponse({'status': 'fail', 'message': 'An unexpected error occurred.'}, status=500)
    return JsonResponse({'status': 'fail', 'message': 'Invalid request method.'}, status=405)

@csrf_exempt
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
def session_data_api(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            weather_info = data.get('weather_info', {})
            request.session['weather_info'] = weather_info
            return JsonResponse({"message": "Weather info saved successfully"})
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON data"}, status=400)
    weather_info = request.session.get('weather_info', 'No weather info in session')
    print(weather_info)
    data = {
        'address': request.session.get('address', 'No address in session'),
        'latitude': request.session.get('latitude', 'No latitude in session'),
        'longitude': request.session.get('longitude', 'No longitude in session'),
        'selectedGender': request.session.get('selectedGender', 'No gender in session'),
        'selectedCity_code': request.session.get('selectedCity_code', 'No city code in session'),
        'selectedDistrict': request.session.get('selectedDistrict', 'No district in session'),
        'selectedLatitude': request.session.get('selectedLatitude', 'No latitude in session'),
        'selectedLongitude': request.session.get('selectedLongitude', 'No longitude in session'),
        'learn_data': request.session.get('learn_data', 'No learn data in session'),
        'weather_info': request.session.get('weather_info', 'No weather info in session')
    }
    
    return JsonResponse(data)
    

@require_POST
@csrf_exempt
def session_delete(request, key=None):
    try:
        if key == 'location':
            del request.session['address']
            del request.session['latitude']
            del request.session['longitude']
            del request.session['selectedCity_code']
            del request.session['selectedDistrict']
            del request.session['selectedLatitude']
            del request.session['selectedLongitude']
        elif key == 'gender':
            del request.session['selectedGender']
        else:
            return JsonResponse({'success': False, 'error': 'Invalid session type'})
        return JsonResponse({'success': True})
    except KeyError:
        return JsonResponse({'success': False, 'error': 'Session key not found'})
    except Exception as e:
        print(f"Error deleting session: {e}")
        return JsonResponse({'success': False, 'error': 'Unknown error occurred'})