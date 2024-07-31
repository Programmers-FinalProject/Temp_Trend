from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json
from weather.models import LocationRecord
from geopy.geocoders import Nominatim


@csrf_exempt
@require_POST
def save_location(request):
    data = json.loads(request.body)
    latitude = data.get('latitude')
    longitude = data.get('longitude')
    location_type = data.get('location_type')

    location = LocationRecord.objects.create(
        latitude=latitude,
        longitude=longitude,
        location_type=location_type
    )

    return JsonResponse({
        'status': 'success',
        'latitude': location.latitude,
        'longitude': location.longitude,
        'location_type': location.location_type
    })
    
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