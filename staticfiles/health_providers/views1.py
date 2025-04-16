# from rest_framework import generics, permissions
# from .models import HealthProvider, Consultation, Appointment
# from .serializers import HealthProviderSerializer, ConsultationSerializer
# from django.shortcuts import render, redirect
# from django.core.mail import send_mail
# from .serializers import AppointmentSerializer
# from django.shortcuts import get_object_or_404, redirect
# from django.contrib import messages
# from django.contrib.auth.decorators import login_required
# from .forms import AppointmentForm, ConsultationRequestForm


# # def send_email_to_provider(request, provider_id):
# #     if request.method == 'POST':
# #         provider = get_object_or_404(HealthProvider, id=provider_id)
# #         user_message = request.POST.get('message')

# #         try:
# #             # Send email to the health provider
# #             send_mail(
# #                 subject=f"Message from {request.user.username}",
# #                 message=user_message,
# #                 from_email=request.user.email,  # Send from the user's email
# #                 recipient_list=[provider.contact_info],  # Send to the provider's email
# #                 fail_silently=False,
# #             )
# #             messages.success(request, "Your message has been sent successfully!")
# #         except Exception as e:
# #             messages.error(request, f"Failed to send message: {e}")

# #     return redirect('health_provider_page')
# @login_required
# def book_appointment(request):
#     if request.method == 'POST':
#         form = AppointmentForm(request.POST)
#         if form.is_valid():
#             appointment = form.save(commit=False)
#             appointment.user = request.user
#             appointment.save()
#             messages.success(request, "Appointment booked successfully!")
#             return redirect('appointment_confirmation')  # Redirect to a confirmation page
#     else:
#         form = AppointmentForm()
#     return render(request, 'book_appointment.html', {'form': form})

# @login_required
# def request_consultation(request):
#     if request.method == 'POST':
#         form = ConsultationRequestForm(request.POST)
#         if form.is_valid():
#             consultation = form.save(commit=False)
#             consultation.user = request.user
#             consultation.save()
#             return redirect('consultation_confirmation')  # Redirect to a confirmation page
#     else:
#         form = ConsultationRequestForm()
#     return render(request, 'request_consultation.html', {'form': form})


# def health_provider_page(request):
#     # Fetch all health providers from the database
#     health_providers = HealthProvider.objects.all()
#     # Pass the data to the template
#     return render(request, 'health_provider.html', {'health_providers': health_providers})


# class HealthProviderList(generics.ListAPIView):
#     queryset = HealthProvider.objects.all()
#     serializer_class = HealthProviderSerializer


# def create_consultation(request, provider_id):
#     if request.method == 'POST':
#         provider = get_object_or_404(HealthProvider, id=provider_id)
#         issue = request.POST.get('issue')

#         # Save consultation to the database
#         consultation = Consultation.objects.create(
#             user=request.user,
#             health_provider=provider,
#             issue=issue
#         )

#         # Send email notification to the health provider
#         try:
#             send_mail(
#                 subject=f"New Consultation Request from {request.user.username}",
#                 message=f"You have a new consultation request from {request.user.username}.\n\nIssue: {issue}",
#                 from_email=request.user.email,  # Send from the user's email
#                 recipient_list=[provider.email],  # Send to the health provider's email
#                 fail_silently=False,
#             )
#             messages.success(request, "Consultation request sent successfully!")
#         except Exception as e:
#             messages.error(request, f"Failed to send consultation request: {e}")

#     return redirect('health_provider_page')

# def create_appointment(request, provider_id):
#     if request.method == 'POST':
#         provider = get_object_or_404(HealthProvider, id=provider_id)
#         date_time = request.POST.get('date_time')
#         notes = request.POST.get('notes')

#         # Save appointment to the database
#         appointment = Appointment.objects.create(
#             user=request.user,
#             health_provider=provider,
#             date_time=date_time,
#             notes=notes
#         )

#         # Send email notification to the health provider
#         try:
#             send_mail(
#                 subject=f"New Appointment Scheduled by {request.user.username}",
#                 message=f"You have a new appointment scheduled by {request.user.username}.\n\nDate and Time: {date_time}\nNotes: {notes}",
#                 from_email=request.user.email,  # Send from the user's email
#                 recipient_list=[provider.email],  # Send to the health provider's email
#                 fail_silently=False,
#             )
#             messages.success(request, "Appointment booked successfully!")
#         except Exception as e:
#             messages.error(request, f"Failed to book appointment: {e}")

#     return redirect('health_provider_page')