from django.urls import path
from . import views

app_name = 'advocates'

urlpatterns = [
    # Main paths
    path('', views.warrior_list, name='warrior_list'),
    path('advocates/', views.default_warrior_detail, name='default_warrior'),
    path('<int:pk>/', views.warrior_detail, name='warrior_detail'),
    # Donation-related paths
    path('donate/', views.initiate_donation, name='initiate_donation'),
    path('donations/history/', views.donation_history, name='donation_history'),
    path('donation/receipt/<int:donation_id>/', views.download_receipt, name='download_receipt'),
    path('donation/success/', views.donation_success, name='donation_success'),
    
    # M-Pesa callback
    path('mpesa-callback/', views.mpesa_callback, name='mpesa_callback'),
    
    # Consultation paths (only one version needed)
    path('consultation/request/', views.request_consultation, name='request_consultation'),
    
    # Appointment paths (only one version needed)
    path('appointments/<int:warrior_id>/', views.book_appointment, name='book_appointment'),
    path('donations/confirm/', views.confirm_payments, name='confirm_payments'),
    path('donations/<int:donation_id>/receipt/', views.download_receipt, name='download_receipt'),
    path('donations/<int:donation_id>/view/', views.view_receipt, name='view_receipt'),
    path('update-status/<int:donation_id>/', views.update_donation_status, name='update_donation_status'),
]




# from django.urls import path
# from . import views

# app_name = 'advocates'

# urlpatterns = [
#     path('', views.warrior_list, name='warrior_list'),
#     path('advocates/consultation/', views.request_consultation, name='request_consultation'),
#     path('appointment/<int:warrior_id>/', views.book_appointment, name='book_appointment'),
#    # path('donate/', views.donate, name='donate'),
#     path('donation/receipt/<int:donation_id>/', views.download_receipt, name='download_receipt'),
#     path('donate/', views.initiate_donation, name='initiate_donation'),
#     path('donations/history/', views.donation_history, name='donation_history'),
#     path('ampesa-callback/', views.mpesa_callback, name='mpesa_callback'),
#     path('consultation/request/', views.request_consultation, name='request_consultation'),
#     path('advocates/appointments/<int:warrior_id>/', views.book_appointment, name='book_appointment'),
#     path('donation/success/', views.donation_success, name='donation_success'),
# ]