# # from django.contrib import admin

# # Register your models here.
# from django.contrib import admin
# from .models import AirQualityRecord  # Import your model

# admin.site.register(AirQualityRecord)  # Register it in admin
from django.contrib import admin
from .models import AirQualityStation, AirQualityReading

@admin.register(AirQualityStation)
class StationAdmin(admin.ModelAdmin):
    list_display = ('name', 'latitude', 'longitude')
    search_fields = ('name',)
    list_per_page = 20

@admin.register(AirQualityReading)
class ReadingAdmin(admin.ModelAdmin):
    list_display = ('station', 'timestamp', 'aqi', 'dominant_pollutant')
    list_filter = ('station', 'dominant_pollutant', 'timestamp')
    search_fields = ('station__name',)
    date_hierarchy = 'timestamp'
    list_per_page = 50
    fieldsets = (
        ('Station Info', {
            'fields': ('station', 'timestamp')
        }),
        ('Air Quality', {
            'fields': ('aqi', 'dominant_pollutant')
        }),
        ('Pollutants', {
            'fields': ('pm25', 'pm10', 'o3', 'no2', 'so2', 'co'),
            'classes': ('collapse',)
        }),
        ('Weather', {
            'fields': ('humidity', 'temperature', 'pressure', 'wind'),
            'classes': ('collapse',)
        })
    )