from django.urls import path
from . import views

app_name = 'air_quality'  # Define the app_name here

urlpatterns = [
    path('', views.air_quality_page, name='air_quality_page'),
    path('api/air-quality-data/', views.get_air_quality_data, name='get_air_quality_data'),
# path('api/historical-data/', views.get_historical_data, name='get_historical_data'),
    path('historical-data/', views.historical_data, name='historical_data'),
]