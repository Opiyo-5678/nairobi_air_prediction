from django.contrib import admin
from .models import HealthProvider, Consultation, Appointment, Payment, Message

admin.site.register(HealthProvider)
admin.site.register(Consultation)
admin.site.register(Appointment)
admin.site.register(Payment)
admin.site.register(Message)
