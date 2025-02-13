# from django.db import models

# Create your models here.
from django.db import models


class HealthProvider(models.Model):
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    phone = models.CharField(max_length=15)