
from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from django.conf import settings
from django.contrib.auth import get_user_model
User = get_user_model()
from django.db import migrations

def remove_donor_email_column(apps, schema_editor):
    with schema_editor.connection.cursor() as cursor:
        cursor.execute("""
            SELECT COUNT(*)
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_NAME = 'advocates_donation'
            AND COLUMN_NAME = 'donor_email'
        """)
        if cursor.fetchone()[0]:
            cursor.execute("ALTER TABLE advocates_donation DROP COLUMN donor_email")

class Migration(migrations.Migration):
    dependencies = [
        ('advocates', 'previous_migration'),
    ]

    operations = [
        migrations.RunPython(
            remove_donor_email_column,
            reverse_code=migrations.RunPython.noop
        ),
    ]

class CleanAirWarrior(models.Model):
    profile_picture = models.ImageField(upload_to='warriors/', blank=True, null=True)
    name = models.CharField(max_length=100)
    expertise = models.CharField(max_length=200)  # e.g., "Indoor Air Quality"
    bio = models.TextField()
    availability = models.CharField(max_length=100)  # e.g., "Mon-Fri, 9AM-5PM"
    email = models.EmailField()

    def __str__(self):
        return self.name

class ConsultationRequest(models.Model):
    warrior = models.ForeignKey(CleanAirWarrior, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    issue = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Consultation from {self.name}"

class Appointment(models.Model):
    warrior = models.ForeignKey(CleanAirWarrior, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    date = models.DateTimeField()  # Use DateTimeField for exact slots
    reason = models.TextField()
    is_confirmed = models.BooleanField(default=False)

    def __str__(self):
        return f"Appointment with {self.warrior.name} on {self.date}"


class Donation(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('failed', 'Failed'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    phone_number = models.CharField(max_length=15)
    date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    mpesa_receipt = models.CharField(max_length=50, blank=True, null=True)
    confirmed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='confirmed_donations')
    confirmation_date = models.DateTimeField(null=True, blank=True)
# donor_email = models.EmailField(blank=True, null=True)
    
    def __str__(self):
        return f"Donation #{self.id} - {self.amount}"
    
    def confirm_payment(self, user, receipt_number=None):
        self.status = 'confirmed'
        self.mpesa_receipt = receipt_number
        self.confirmed_by = user
        self.confirmation_date = timezone.now()
        self.save()
        
    def generate_receipt(self):
        """Generate receipt text (we'll use this for PDF generation)"""
        return f"""
        Clean Air Initiative - Donation Receipt
        ----------------------------------------
        Receipt No: {self.id}
        Date: {self.date.strftime('%Y-%m-%d %H:%M')}
        Amount: KES {self.amount:.2f}
        Phone: {self.phone_number}
        Status: {self.get_status_display()}
        Confirmed by: {self.confirmed_by.get_full_name() if self.confirmed_by else 'System'}
        Confirmation date: {self.confirmation_date.strftime('%Y-%m-%d %H:%M') if self.confirmation_date else 'N/A'}
        MPesa Receipt: {self.mpesa_receipt or 'N/A'}
        ----------------------------------------
        Thank you for your donation!
        """
        

