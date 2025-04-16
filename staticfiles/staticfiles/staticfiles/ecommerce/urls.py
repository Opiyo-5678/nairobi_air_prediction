from django.urls import path
from .views import ProductListView, OrderCreateView
from .views import initiate_payment, MpesaCallbackView, ProductListView, OrderCreateView  
urlpatterns = [
    path('products/', ProductListView.as_view(), name='products'),
    path('order/', OrderCreateView.as_view(), name='order'),
    path("mpesa/pay/", initiate_payment, name="mpesa_payment"),
    path("mpesa/callback/", MpesaCallbackView.as_view(), name="mpesa_callback"),
]