from django.contrib import admin
from .models import LocationRecord

class LocationRecordAdmin(admin.ModelAdmin):
    pass

admin.site.register(LocationRecord,LocationRecordAdmin)