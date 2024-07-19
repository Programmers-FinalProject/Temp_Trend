<<<<<<< HEAD
from django.contrib import admin

# Register your models here.
=======
from django.contrib import admin
from .models import LocationRecord

class LocationRecordAdmin(admin.ModelAdmin):
    pass

admin.site.register(LocationRecord,LocationRecordAdmin)
>>>>>>> origin
