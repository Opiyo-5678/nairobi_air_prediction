# models.py
from django.db import models

class AirQualityStation(models.Model):
    name = models.CharField(max_length=100)
    latitude = models.FloatField()
    longitude = models.FloatField()
    
    def __str__(self):
        return self.name

class AirQualityReading(models.Model):
    station = models.ForeignKey(AirQualityStation, on_delete=models.CASCADE, related_name='readings')
    timestamp = models.DateTimeField()
    aqi = models.IntegerField(null=True, blank=True)
    dominant_pollutant = models.CharField(max_length=50, null=True, blank=True)
    
    # Specific pollutants
    pm25 = models.FloatField(null=True, blank=True)
    pm10 = models.FloatField(null=True, blank=True)
    o3 = models.FloatField(null=True, blank=True)
    no2 = models.FloatField(null=True, blank=True)
    so2 = models.FloatField(null=True, blank=True)
    co = models.FloatField(null=True, blank=True)
    humidity = models.FloatField(null=True, blank=True)
    temperature = models.FloatField(null=True, blank=True)
    pressure = models.FloatField(null=True, blank=True)
    wind = models.FloatField(null=True, blank=True)
    
    class Meta:
        # This ensures we don't have duplicate readings for the same time and station
        unique_together = ('station', 'timestamp')
    
    def __str__(self):
        return f"{self.station.name} - AQI: {self.aqi} - {self.timestamp}"