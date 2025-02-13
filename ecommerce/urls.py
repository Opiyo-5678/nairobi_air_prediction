from django.urls import path
from .views import ProductListView, OrderCreateView

urlpatterns = [
    path('products/', ProductListView.as_view(), name='products'),
    path('order/', OrderCreateView.as_view(), name='order'),
]