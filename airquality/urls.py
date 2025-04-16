from django.contrib import admin
from django.urls import path, include
from .import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('authentication.urls')),
   # path('chatbot/', include('chatbot.urls')),
    path('air-quality/', include("air_quality.urls", namespace="air_quality")),  # ✅ Correct way to include app URLs
    path('health-providers/', include('health_providers.urls')),
    path('ecommerce/', include('ecommerce.urls')),
    path('', views.index, name='index'),
    path('advocates/', include('advocates.urls', namespace='advocates')),
    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
