from rest_framework import serializers
from .models import HealthProvider, Consultation, Appointment

class HealthProviderSerializer(serializers.ModelSerializer):
    class Meta:
        model = HealthProvider
        fields = '__all__'

class ConsultationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Consultation
        fields = '__all__'

class AppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = '__all__'