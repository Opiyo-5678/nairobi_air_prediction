from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator

class HealthProvider(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE) 
    name = models.CharField(max_length=100)
    specialization = models.CharField(max_length=100)
    email = models.EmailField()
    contact_info = models.CharField(max_length=100)
    bio = models.TextField()
    profile_pic = models.ImageField(upload_to='health_provider_profile_pics/', blank=True, null=True)
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Added consultation fee
    appointment_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)   # Added appointment fee

    def __str__(self):
        return self.name


class Consultation(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    health_provider = models.ForeignKey('HealthProvider', on_delete=models.CASCADE)
    patient_name = models.CharField(max_length=100)  # Added patient name
    patient_email = models.EmailField()  # Added patient email
    issue = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    is_paid = models.BooleanField(default=False)
    payment_reference = models.CharField(max_length=100, blank=True)
    email_sent = models.BooleanField(default=False)
    consultation_fee = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )  # Added consultation fee

    def __str__(self):
        return f"Consultation by {self.user.username} with {self.health_provider.name}"


class Appointment(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    health_provider = models.ForeignKey('HealthProvider', on_delete=models.CASCADE)
    patient_name = models.CharField(max_length=100)  # Added patient name
    patient_email = models.EmailField()  # Added patient email
    date_time = models.DateTimeField()
    reason = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    is_paid = models.BooleanField(default=False)
    payment_reference = models.CharField(max_length=100, blank=True)
    email_sent = models.BooleanField(default=False)
    appointment_fee = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )  # Added appointment fee

    def __str__(self):
        return f"Appointment with {self.health_provider.name} on {self.date_time}"


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
    receipt_number = models.CharField(max_length=50, blank=True, null=True)  # Added receipt number
    payment_method = models.CharField(max_length=50, default='M-Pesa')  # Added payment method
    
    def __str__(self):
        return f"Payment {self.reference} by {self.user.username} - {self.status}"


class Receipt(models.Model):
    payment = models.OneToOneField('Payment', on_delete=models.CASCADE)
    generated_at = models.DateTimeField(auto_now_add=True)
    receipt_number = models.CharField(max_length=50, unique=True)
    pdf_file = models.FileField(upload_to='receipts/', blank=True, null=True)  # For storing PDF receipts
    
    def __str__(self):
        return f"Receipt {self.receipt_number} for Payment {self.payment.reference}"


class EmailLog(models.Model):
    recipient = models.EmailField()
    subject = models.CharField(max_length=255)
    sent_at = models.DateTimeField(auto_now_add=True)
    was_successful = models.BooleanField(default=False)
    related_consultation = models.ForeignKey('Consultation', on_delete=models.SET_NULL, null=True, blank=True)
    related_appointment = models.ForeignKey('Appointment', on_delete=models.SET_NULL, null=True, blank=True)
    
    def __str__(self):
        return f"Email to {self.recipient} at {self.sent_at}"
    
