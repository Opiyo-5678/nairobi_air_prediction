from django.contrib import admin
from .models import HealthProvider, Consultation, Appointment

admin.site.register(HealthProvider)
admin.site.register(Consultation)
admin.site.register(Appointment)