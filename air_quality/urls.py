from django.urls import path
from . import views

app_name = 'air_quality'  # Define the app_name here

urlpatterns = [
    # path('', views.index, name='index'),
    path('', views.air_quality_page, name='air_quality_page'),
    path('api/air-quality-data/', views.get_air_quality_data, name='get_air_quality_data'),
# path('api/historical-data/', views.get_historical_data, name='get_historical_data'),
    path('historical-data/', views.historical_data, name='historical_data'),
  #  path('air-quality/', views.air_quality_api, name='air_quality'),
  #  path('air-quality/data/', views.get_historical_data, name='air_quality_data'),
    path('api/air-quality/', views.air_quality_api, name='air_quality_api'),
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    path('terms-of-service/', views.terms_of_service, name='terms_of_service'),
    path('contact-us/', views.contact_us, name='contact_us'),
    path('contact-success/', views.contact_success, name='contact_success'),
    path('generate-report/', views.GeneratePDFView.as_view(), name='generate_report'),
    
  
    
]