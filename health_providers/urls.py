from django.urls import path
from .views import HealthProvidersView

urlpatterns = [
    path('nearby/', HealthProvidersView.as_view(), name='nearby'),
]