# air_quality/views.py
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse

def index(request):
    return render(request, 'index.html')
