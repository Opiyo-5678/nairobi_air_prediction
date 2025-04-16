from django.db import models
from django.conf import settings



class HealthProvider(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE) 
    name = models.CharField(max_length=100)
    specialization = models.CharField(max_length=100)
    email = models.EmailField()  # Add this field
    contact_info = models.CharField(max_length=100)
    bio = models.TextField()

    def __str__(self):
        return self.name


class Consultation(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    health_provider = models.ForeignKey('HealthProvider', on_delete=models.CASCADE)
    issue = models.TextField(blank=True, null=True)                    # blank=True, null=True
    
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='Pending')

    def __str__(self):
        return f"Consultation by {self.user.username} with {self.health_provider.name}"


class Appointment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    health_provider = models.ForeignKey('HealthProvider', on_delete=models.CASCADE)
    date_time = models.DateTimeField()
    reason = models.TextField(blank=True, null=True)                    # blank=True, null=True
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='Pending')

    def __str__(self):
        return f"Appointment with {self.health_provider.name} on {self.date_time}"