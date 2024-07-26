from django.contrib import admin
from .models import LocationRecord,WeatherData

class LocationRecordAdmin(admin.ModelAdmin):
    list_display = ('latitude', 'longitude', 'location_type', 'created_at')

admin.site.register(LocationRecord,LocationRecordAdmin)



@admin.register(WeatherData)
class WeatherDataAdmin(admin.ModelAdmin):
    list_display = ('basedate', 'basetime', 'weather_code', 'fcstdate', 'fcsttime', 'fcstvalue', 'nx', 'ny')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.using('redshift')


