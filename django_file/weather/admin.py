from django.contrib import admin
from .models import LocationRecord,WeatherData,WeatherStation

class LocationRecordAdmin(admin.ModelAdmin):
    list_display = ('latitude', 'longitude', 'location_type', 'created_at')

admin.site.register(LocationRecord,LocationRecordAdmin)



@admin.register(WeatherData)
class WeatherDataAdmin(admin.ModelAdmin):
    list_display = ('basedate', 'basetime', 'weather_code', 'fcstdate', 'fcsttime', 'fcstvalue', 'nx', 'ny')

    def get_queryset(self, request):
        """
        Redshift 데이터베이스에서 WeatherData 쿼리셋을 가져옴
        """
        qs = super().get_queryset(request)
        return qs.using('redshift')


@admin.register(WeatherStation)
class WeatherStationAdmin(admin.ModelAdmin):
    list_display = ('basin', 'law_id', 'fct_id', 'stn_en', 'stn_ko')

    def get_queryset(self, request):
        """
        Redshift 데이터베이스에서 WeatherStation 쿼리셋을 가져옴
        """
        qs = super().get_queryset(request)
        return qs.using('redshift')
