from django.db import models
from django.conf import settings



class HealthProvider(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE) 
    name = models.CharField(max_length=100)
    specialization = models.CharField(max_length=100)
    email = models.EmailField()
    contact_info = models.CharField(max_length=100)
    bio = models.TextField()
    profile_pic = models.ImageField(upload_to='health_provider_profile_pics/', blank=True, null=True)  # Add this line

    def __str__(self):
        return self.name


class Consultation(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    health_provider = models.ForeignKey('HealthProvider', on_delete=models.CASCADE)
    issue = models.TextField(blank=True, null=True)                    # blank=True, null=True
    
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='Pending')
    is_paid = models.BooleanField(default=False)
    payment_reference = models.CharField(max_length=100, blank=True)
    email_sent = models.BooleanField(default=False)

    def __str__(self):
        return f"Consultation by {self.user.username} with {self.health_provider.name}"


class Appointment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    health_provider = models.ForeignKey('HealthProvider', on_delete=models.CASCADE)
    date_time = models.DateTimeField()
    reason = models.TextField(blank=True, null=True)                    # blank=True, null=True
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='Pending')
    is_paid = models.BooleanField(default=False)
    payment_reference = models.CharField(max_length=100, blank=True)
    email_sent = models.BooleanField(default=False)

    def __str__(self):
        return f"Appointment with {self.health_provider.name} on {self.date_time}"
    
    
    # models.py - Add this Payment model to your existing models.py file



# Your existing models remain unchanged

class Payment(models.Model):
    PAYMENT_FOR_CHOICES = [
        ('appointment', 'Appointment'),
        ('consultation', 'Consultation'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    health_provider = models.ForeignKey('HealthProvider', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    reference = models.CharField(max_length=100, unique=True)
    payment_for = models.CharField(max_length=20, choices=PAYMENT_FOR_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    phone_number = models.CharField(max_length=15)
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Payment {self.reference} by {self.user.username} - {self.status}"
    


    

class Message(models.Model):
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_messages')
    consultation = models.ForeignKey('Consultation', on_delete=models.CASCADE, null=True, blank=True)
    appointment = models.ForeignKey('Appointment', on_delete=models.CASCADE, null=True, blank=True)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.sender} to {self.receiver}"