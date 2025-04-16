from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.views.decorators.csrf import csrf_protect
from .serializers import UserSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .forms import RegistrationForm
from django.utils.crypto import get_random_string
from django.contrib.auth.forms import AuthenticationForm
from django.urls import reverse
from django.contrib.auth.views import LogoutView
from django.views import View

User = get_user_model()


def register_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            user = User.objects.create(username=username, email=email)  #
            user.set_password(password)  # Hash password separately
            user.save()

            return redirect('/auth/login/')  # Redirect to index after 
    else:
        form = RegistrationForm()

    return render(request, 'register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')

            user = authenticate(request, username=email, password=password)

            if user is not None and user.check_password(password):
                login(request, user)
                next_url = request.GET.get('next', 'air_quality:air_quality_page')  # Use URL name
                print(f"Next URL: {next_url}")  # Debugging
                return redirect(next_url)
            else:
                error_message = "Invalid username or password."
                return render(request, 'login.html', {'error_message': error_message})
        else:
            error_message = "Invalid form submission."
            return render(request, 'login.html', {'error_message': error_message})
    else:
        form = AuthenticationForm()
        next_param = request.GET.get('next', 'Not provided')
        print(f"Next parameter in GET request: {next_param}")  # Debugging
        return render(request, 'login.html', {'form': form})


class CustomLogoutView(View):
    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect('/auth/login/')
    