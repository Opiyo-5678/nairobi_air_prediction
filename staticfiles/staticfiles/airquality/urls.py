from django.contrib import admin
from django.urls import path, include
from airquality.views import index

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('authentication.urls')),
   # path('chatbot/', include('chatbot.urls')),
    path('air-quality/', include("air_quality.urls", namespace="air_quality")),  # ✅ Correct way to include app URLs
    path('health-providers/', include('health_providers.urls')),
    path('ecommerce/', include('ecommerce.urls')),
    path('', index, name='index'),
]
