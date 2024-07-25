from django.db import models

class LocationRecord(models.Model):
    latitude = models.DecimalField(max_digits=15, decimal_places=8)
    longitude = models.DecimalField(max_digits=15, decimal_places=8)
    location_type = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        app_label = 'weather'

    def __str__(self):
        return f"위치정보 : {self.location_type} | 위도 :({self.latitude}, 경도 :{self.longitude})"

class WeatherData(models.Model):
    basedate = models.CharField(max_length=10, help_text="기준 날짜")
    basetime = models.CharField(max_length=10, help_text="기준 시간")
    weather_code = models.CharField(max_length=10, help_text="날씨 코드")
    fcstdate = models.CharField(max_length=10, help_text="예보 날짜")
    fcsttime = models.CharField(max_length=10, help_text="예보 시간")
    fcstvalue = models.CharField(max_length=10, help_text="예보 값")
    nx = models.CharField(max_length=3, help_text="nx")
    ny = models.CharField(max_length=3, help_text="ny")
    
    class Meta:
        app_label = 'weather'
        
    def __str__(self):
        return f"예보 일 : {self.basedate} | 예보 시 :{self.basetime} | 코드 : {self.weather_code} | 예보 일 : {self.fcstdate} | 예보 시 : {self.fcsttime} | 예보 값 {self.fcstvalue} | 예보 지역{self.nx},{self.ny}"
