from django.contrib.auth.models import AbstractUser
from django.db import models
import random
from datetime import timedelta, datetime

class User(AbstractUser):
    email = models.EmailField(unique=True)
    is_verified = models.BooleanField(default=False)
    otp = models.CharField(max_length=6, blank=True, null=True)
    otp_created_at = models.DateTimeField(blank=True, null=True)  # Track OTP creation time

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def generate_otp(self):
        """Generate a 6-digit OTP and store it with a timestamp."""
        self.otp = str(random.randint(100000, 999999))
        self.otp_created_at = datetime.now()
        self.save()
        return self.otp

    def verify_otp(self, otp):
        """Check if OTP is valid and within 10 minutes."""
        if self.otp and self.otp == otp:
            if self.otp_created_at and (datetime.now() - self.otp_created_at) < timedelta(minutes=10):
                self.is_verified = True
                self.otp = None  # Clear OTP after successful verification
                self.otp_created_at = None
                self.save()
                return True
        return False  # Invalid OTP

    def __str__(self):
        return self.username
