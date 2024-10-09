from django.contrib import admin

# Register your models here.


from django.contrib import admin
from .models import EmergencyCall

@admin.register(EmergencyCall)
class EmergencyCallAdmin(admin.ModelAdmin):
    list_display = ('id', 'call_status', 'user_location', 'timestamp')
    search_fields = ('user_location',)
    list_filter = ('call_status', 'timestamp')

