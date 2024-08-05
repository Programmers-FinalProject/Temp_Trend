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
    nx = models.CharField(max_length=3, help_text="nx", primary_key=True)
    ny = models.CharField(max_length=3, help_text="ny")
    
    class Meta:
        app_label = 'weather'
        managed = False
        db_table = 'weather_data'
        
    def __str__(self):
        return f"예보 일 : {self.basedate} | 예보 시 :{self.basetime} | 코드 : {self.weather_code} | 예보 일 : {self.fcstdate} | 예보 시 : {self.fcsttime} | 예보 값 {self.fcstvalue} | 예보 지역{self.nx},{self.ny}"

class musinsaData(models.Model):
    product_name = models.TextField(primary_key=True)
    product_link = models.TextField()
    image_link = models.TextField()
    rank = models.IntegerField()
    date = models.DateTimeField()
    data_creation_time = models.DateTimeField()
    category = models.TextField()
    price = models.IntegerField()
    gender = models.TextField()

    class Meta:
        app_label = 'weather'
        db_table = 'musinsa'
        managed = False

    def __str__(self):
        return f"상품명 : {self.product_name} | 상품링크 : {self.product_link} | 이미지링크 : {self.image_link} | 순위 : {self.rank} | 카테고리 : {self.category} | 가격 : {self.price} | 성별 : {self.gender}"
 
class weatherCategorizeData(models.Model):
    id = models.AutoField(primary_key=True)
    weather_info = models.TextField()
    category = models.TextField()

    class Meta:
        app_label = 'weather'
        db_table = 'weather_categorize'
        managed = False

    def __str__(self):
        return f"id : {self.id} | 날씨정보 : {self.weather_info} | 카테고리 : {self.category}"