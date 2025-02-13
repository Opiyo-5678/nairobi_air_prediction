# from django.shortcuts import render

# Create your views here.
from rest_framework import generics
from .models import Product, Order
from .serializers import ProductSerializer, OrderSerializer


class ProductListView(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class OrderCreateView(generics.CreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer