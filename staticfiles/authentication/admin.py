# from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import User  # Import your custom User model

admin.site.register(User)  # ✅ Register your User model
