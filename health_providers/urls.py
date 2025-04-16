


from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Health Provider Pages
    path('', views.health_provider_page, name='health_provider_page'),
    path('dashboard/', views.health_provider_dashboard, name='health_provider_dashboard'),

    # API Endpoints
    path('api/health-providers/', views.HealthProviderList.as_view(), name='health_provider_api'),

    # Service Creation Views
    path('create-consultation/<int:provider_id>/', views.create_consultation, name='create_consultation'),
    path('create-appointment/<int:provider_id>/', views.create_appointment, name='create_appointment'),
    
    # Confirmation Pages
    path('appointment/confirmation/', views.appointment_confirmation, name='appointment_confirmation'),
    path('consultation/confirmation/', views.consultation_confirmation, name='consultation_confirmation'),

    # Messaging System
    path('messages/send/consultation/<int:consultation_id>/', views.send_message, name='send_consultation_message'),
    path('messages/send/appointment/<int:appointment_id>/', views.send_message, name='send_appointment_message'),
    path('messages/', views.view_messages, name='view_messages'),

    # Payment Processing Flow
   # path('payments/initiate/', views.initiate_payment, name='initiate_payment'),
  #  path('payments/processing/', views.payment_processing, name='payment_processing'),
    path('payments/check-status/', views.check_payment_status, name='check_payment_status'),
    
    # Payment Webhook
   # path('payments/mpesa-callback/', views.mpesa_callback, name='mpesa_callback'),
    path('confirm-payment/', views.confirm_payment, name='confirm_payment'),
    path('pyment_history', views.payment_history, name='payment_history'),
    path('make_payment/', views.make_payment, name='make_payment'),
    path('pay/', views.pay, name='pay'),
    path('stk/', views.stk, name='stk'),
    path('token/', views.token, name='token'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
# from django.urls import path
# from . import views
# from django.conf import settings
# from django.conf.urls.static import static

# urlpatterns = [
#     # Health Provider Pages
#     path('', views.health_provider_page, name='health_provider_page'),
#     path('dashboard/', views.health_provider_dashboard, name='health_provider_dashboard'),

#     # API Endpoints
#     path('api/health-providers/', views.HealthProviderList.as_view(), name='health_provider_api'),

#     # Appointment and Consultation Views
#     path('create-consultation/<int:provider_id>/', views.create_consultation, name='create_consultation'),
#     path('create-appointment/<int:provider_id>/', views.create_appointment, name='create_appointment'),
#     path('appointment-confirmation/', views.appointment_confirmation, name='appointment_confirmation'),
#     path('consultation-confirmation/', views.consultation_confirmation, name='consultation_confirmation'),

#     # Messaging System
#     path('send_message/<int:consultation_id>/', views.send_message, name='send_message'),
#     path('send_message/<int:appointment_id>/', views.send_message, name='send_message'),
#     path('view_messages/', views.view_messages, name='view_messages'),

#     # Payment Views
#     path('initiate-payment/', views.initiate_payment, name='initiate_payment'),
#     path('payment-processing/', views.payment_processing, name='payment_processing'),
#     path('check-payment-status/', views.check_payment_status, name='check_payment_status'),
#     path('mpesa-callback/', views.mpesa_callback, name='mpesa_callback'),
#   #  path('consultation/<int:pk>/pay/', views.initiate_service_payment, {'service_type': 'consultation'}, name='pay_consultation'),
#    # path('appointment/<int:pk>/pay/', views.initiate_service_payment, {'service_type': 'appointment'}, name='pay_appointment'),
# ]



# if settings.DEBUG:
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

