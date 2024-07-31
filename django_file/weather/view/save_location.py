from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json
from weather.models import LocationRecord
from geopy.geocoders import Nominatim


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
        location_record = LocationRecord(
            latitude=latitude,
            longitude=longitude,
            location_type=location_type,
            session=session_key
        )
        location_record.save()

        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)

@csrf_exempt
@require_POST
def location_name(request):
    data = json.loads(request.body)
    latitude = data.get('latitude')
    longitude = data.get('longitude')
    
    geolocator = Nominatim(user_agent="geoapiExercises")
    location = geolocator.reverse((latitude, longitude), language='ko')
    address = location.address if location else "주소를 찾을 수 없습니다."
    
    return JsonResponse({'address': address})