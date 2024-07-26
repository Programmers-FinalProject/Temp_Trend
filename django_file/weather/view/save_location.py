from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json
from weather.models import LocationRecord

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