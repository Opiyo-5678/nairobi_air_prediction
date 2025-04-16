from django import forms
from .models import ConsultationRequest, Appointment, Donation

class ConsultationForm(forms.ModelForm):
    class Meta:
        model = ConsultationRequest
        fields = ['name', 'email', 'issue']

class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['name', 'email', 'date', 'reason']


class DonationForm(forms.ModelForm):
    class Meta:
        model = Donation
        fields = ['amount', 'phone_number']
        widgets = {
            'phone_number': forms.TextInput(attrs={
                'placeholder': '2547XXXXXXXX',
                'pattern': '^254\d{9}$',
                'title': 'Format: 2547XXXXXXXX'
            }),
            'amount': forms.NumberInput(attrs={
                'min': '10',
                'step': '10'
            })
        }