<<<<<<< HEAD
from django.contrib import admin

# Register your models here.
=======
from django.contrib import admin
from .models import LocationRecord

class LocationRecordAdmin(admin.ModelAdmin):
    pass

admin.site.register(LocationRecord,LocationRecordAdmin)
<<<<<<< HEAD
>>>>>>> origin
=======
>>>>>>> 6c633ae2298c44abf0fa8b343f7118d5c1ff1e85
>>>>>>> main
