from django.db import models

class LocationRecord(models.Model):
    latitude = models.DecimalField(max_digits=15, decimal_places=8)
    longitude = models.DecimalField(max_digits=15, decimal_places=8)
    location_type = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"위치정보 : {self.location_type} | 위도 :({self.latitude}, 경도 :{self.longitude})"
