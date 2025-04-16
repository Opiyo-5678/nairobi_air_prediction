from django.urls import path
from . import views
from .views import CustomLogoutView
app_name = 'authentication'  # Important for namespacing

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
]