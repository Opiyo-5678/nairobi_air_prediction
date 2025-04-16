# from django.urls import path
# from .views import HealthProviderList, ConsultationCreate, AppointmentCreate
# from .views import health_provider_page, send_email_to_provider


# urlpatterns = [
#     path('', health_provider_page, name='health_provider'),
#     path('providers/', HealthProviderList.as_view(), name='health_provider_list'),
#     path('consultations/', ConsultationCreate.as_view(), name='consultation_create'),
#     path('appointments/', AppointmentCreate.as_view(), name='appointment_create'),
#     path('send-email/<int:provider_id>/', send_email_to_provider, name='send_email_to_provider'),
# ]

from django.urls import path
from . import views

urlpatterns = [
    path('health-providers/', views.health_provider_page, name='health_provider_page'),
    path('create-consultation/<int:provider_id>/', views.create_consultation, name='create_consultation'),
    path('create-appointment/<int:provider_id>/', views.create_appointment, name='create_appointment'),
    path('book-appointment/', views.book_appointment, name='book_appointment'),
    path('request-consultation/', views.request_consultation, name='request_consultation'),
    path('appointment-confirmation/', views.appointment_confirmation, name='appointment_confirmation'),
    path('consultation-confirmation/', views.consultation_confirmation, name='consultation_confirmation'),
    path('dashboard/', views.health_provider_dashboard, name='health_provider_dashboard')
]