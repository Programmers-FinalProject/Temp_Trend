from django.contrib import admin
from .models import LocationRecord,WeatherData,WeatherStation,raw_data_WeatherStn

class LocationRecordAdmin(admin.ModelAdmin):
    list_display = ('latitude', 'longitude', 'location_type', 'created_at')

admin.site.register(LocationRecord,LocationRecordAdmin)



@admin.register(WeatherData)
class WeatherDataAdmin(admin.ModelAdmin):
    list_display = ('basedate', 'basetime', 'weather_code', 'fcstdate', 'fcsttime', 'fcstvalue', 'nx', 'ny')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.using('redshift')


@admin.register(WeatherStation)
class WeatherStationAdmin(admin.ModelAdmin):
    list_display = ('basin', 'law_id', 'fct_id', 'stn_en', 'stn_ko')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.using('redshift')

@admin.register(raw_data_WeatherStn)
class WeatherStationAdmin(admin.ModelAdmin):
    list_display = ('stn', 'lon', 'lat', 'stn_sp', 'ht', 'ht_pa', 'ht_ta', 'ht_wd', 'ht_rn', 'stn_ko', 'stn_en', 'fct_id', 'law_id', 'basin')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.using('redshift')
