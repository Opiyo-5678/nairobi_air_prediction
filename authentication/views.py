# from django.shortcuts import render

# Create your views here.
from rest_framework import generics, permissions
from .serializers import UserSerializer
from django.contrib.auth import get_user_model


User = get_user_model()


class SignupView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class LoginView(generics.GenericAPIView):
    # Implement login logic here (use Django REST Framework's TokenAuthentication)
    pass