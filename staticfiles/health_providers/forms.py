from django import forms
from .models import Appointment, Consultation


class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['health_provider', 'date_time', 'reason']
        widgets = {
            'date_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'reason': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Enter the reason for the appointment'}),
        }


class ConsultationRequestForm(forms.ModelForm):
    class Meta:
        model = Consultation
        fields = ['health_provider', 'issue']