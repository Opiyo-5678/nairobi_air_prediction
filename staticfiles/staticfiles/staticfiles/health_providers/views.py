from rest_framework import generics, permissions
from .models import HealthProvider, Consultation, Appointment
from .serializers import HealthProviderSerializer, ConsultationSerializer, AppointmentSerializer
from django.shortcuts import render, redirect, get_object_or_404
from django.core.mail import send_mail
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import AppointmentForm, ConsultationRequestForm


@login_required (login_url='/auth/login/')
def book_appointment(request):
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.user = request.user
            appointment.save()
            messages.success(request, "Appointment booked successfully!")
            return redirect('appointment_confirmation')  # Redirect to a confirmation page
    else:
        form = AppointmentForm()
    return render(request, 'book_appointment.html', {'form': form})


@login_required (login_url='/auth/login/')
def request_consultation(request):
    if request.method == 'POST':
        form = ConsultationRequestForm(request.POST)
        if form.is_valid():
            consultation = form.save(commit=False)
            consultation.user = request.user
            consultation.save()
            messages.success(request, "Consultation request sent successfully!")
            return redirect('consultation_confirmation')  # Redirect to a confirmation page
    else:
        form = ConsultationRequestForm()
    return render(request, 'request_consultation.html', {'form': form})


@login_required(login_url='/auth/login/')
def health_provider_page(request):
    health_providers = HealthProvider.objects.all()
    return render(request, 'health_provider.html', {'health_providers': health_providers})


class HealthProviderList(generics.ListAPIView):
    queryset = HealthProvider.objects.all()
    serializer_class = HealthProviderSerializer


@login_required(login_url='/auth/login/')
def appointment_confirmation(request):
    return render(request, 'appointment_confirmation.html')


@login_required(login_url='/auth/login/')
def consultation_confirmation(request):
    return render(request, 'consultation_confirmation.html')


@login_required(login_url='/auth/login/')
def create_consultation(request, provider_id):
    if request.method == 'POST':
        provider = get_object_or_404(HealthProvider, id=provider_id)
        issue = request.POST.get('issue')

        # Create the consultation instance
        Consultation.objects.create(
            user=request.user,
            health_provider=provider,
            issue=issue
        )

        # Send email notification to the health provider
        try:
            send_mail(
                subject=f"New Consultation Request from {request.user.username}",
                message=f"You have a new consultation request from {request.user.username}.\n\nIssue: {issue}",
                from_email=request.user.email,
                recipient_list=[provider.email],
                fail_silently=False,
            )
            messages.success(request, "Consultation request sent successfully!")
        except Exception as e:
            messages.error(request, f"Failed to send consultation request: {e}")

        # Redirect to the health provider page or a confirmation page
        return redirect('consultation_confirmation')  # Redirect to a confirmation page

    return redirect('health_provider_page')  # Redirect if not a POST request


@login_required(login_url='/auth/login/')
def create_appointment(request, provider_id):
    if request.method == 'POST':
        provider = get_object_or_404(HealthProvider, id=provider_id)
        date_time = request.POST.get('date_time')
        reason = request.POST.get('reason')

        # Create the appointment instance
        Appointment.objects.create(
            user=request.user,
            health_provider=provider,
            date_time=date_time,
            reason=reason
        )

        # Send email notification to the health provider
        try:
            send_mail(
                subject=f"New Appointment Scheduled by {request.user.username}",
                message=f"You have a new appointment scheduled by {request.user.username}.\n\nDate and Time: {date_time}\nReason: {reason}",
                from_email=request.user.email,
                recipient_list=[provider.email],
                fail_silently=False,
            )
            messages.success(request, "Appointment booked successfully!")
        except Exception as e:
            messages.error(request, f"Failed to book appointment: {e}")

        # Redirect to the health provider page or a confirmation page
        return redirect('appointment_confirmation')  # Redirect to a confirmation page

    return redirect('health_provider_page')  # Redirect if not a POST request


@login_required(login_url='/auth/login/')
def health_provider_dashboard(request):
    # Assuming the logged-in user is a health provider
    #  health_provider = get_object_or_404(HealthProvider, user=request.user)

    health_provider = HealthProvider.objects.get(user=request.user)
    consultation_requests = Consultation.objects.filter(health_provider=health_provider, status='Pending')
    return render(request, 'health_provider_dashboard.html', {'consultation_requests': consultation_requests})