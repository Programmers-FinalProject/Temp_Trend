from django.contrib import admin
from .models import LocationRecord,WeatherData,musinsaData

class LocationRecordAdmin(admin.ModelAdmin):
    list_display = ('latitude', 'longitude', 'location_type', 'created_at')

admin.site.register(LocationRecord,LocationRecordAdmin)



@admin.register(WeatherData)
class WeatherDataAdmin(admin.ModelAdmin):
    list_display = ('basedate', 'basetime', 'weather_code', 'fcstdate', 'fcsttime', 'fcstvalue', 'nx', 'ny')
    list_filter = ('basedate', 'weather_code', 'fcstdate')
    search_fields = ('basedate', 'weather_code', 'fcstdate', 'fcstvalue')
    ordering = ('-basedate', '-basetime')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.using('redshift')


@admin.register(musinsaData)
class MusinsaDataAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'rank', 'category', 'price', 'gender', 'date')
    list_filter = ('category', 'gender', 'date')
    search_fields = ('product_name', 'category')
    ordering = ('rank', 'date')
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.using('redshift')