from django.urls import path
from .views import AirQualityView

urlpatterns = [
    path('predict/', AirQualityView.as_view(), name='predict'),
]