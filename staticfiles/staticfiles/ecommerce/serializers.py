from rest_framework import serializers
from .models import Product, Order  # Ensure you have these models in `ecommerce/models.py`


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'
