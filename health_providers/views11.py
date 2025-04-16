# views.py - Update your existing views.py with these changes

from rest_framework import generics, permissions
from .models import HealthProvider, Consultation, Appointment, Payment
from .serializers import HealthProviderSerializer, ConsultationSerializer, AppointmentSerializer
from django.shortcuts import render, redirect, get_object_or_404
from django.core.mail import send_mail
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import AppointmentForm, ConsultationRequestForm
from .mpesa import MpesaAPI
import uuid
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.urls import reverse
from django.conf import settings
import logging
from .models import Payment


logger = logging.getLogger(__name__)
# Initialize M-Pesa API with your credentials
mpesa_api = MpesaAPI(
    consumer_key="p6K0xADABjX4RcZkeJMSOhGGTLeNZx1NWZ3dKM0xw32FJGpp",
    consumer_secret="QuH0qNG7WtI78maGF8W3QYSuqgEKWSGvTgmaHxAL2v7XRmMAY3mDvrAckwDA7K0Z",
    business_shortcode="174379",
    passkey="bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919",
    callback_url="https://mydomain.com/path",  # Make sure to update this with your actual callback URL
    environment="sandbox"  # Use "production" for live environment
)

# Keep your existing views unchanged

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

# Add new payment-related views


@login_required(login_url='/auth/login/')
def initiate_payment(request):
    logger.info("Initiating payment...")
    if request.method == 'POST':
        provider_id = request.POST.get('provider_id')
        payment_for = request.POST.get('payment_for')
        phone_number = request.POST.get('phone_number')
        
        if not all([provider_id, payment_for, phone_number]):
            messages.error(request, "Missing required fields.")
            return redirect('health_provider_page')
        
        provider = get_object_or_404(HealthProvider, id=provider_id)
        
        # Determine payment amount based on service type
        if payment_for == 'appointment':
            amount = 1  # Set your appointment fee
            description = f"Appointment with {provider.name}"
        else:  # consultation
            amount = 1  # Set your consultation fee
            description = f"Consultation with {provider.name}"
        
        # Generate unique reference
        reference = f"HEALTH-{uuid.uuid4().hex[:8].upper()}"
        
        # Create a pending payment record
        payment = Payment.objects.create(
            user=request.user,
            health_provider=provider,
            amount=amount,
            reference=reference,
            payment_for=payment_for,
            phone_number=phone_number,
            status='pending'
        )
        
        # Initiate STK Push
        stk_push_response = mpesa_api.initiate_stk_push(
            phone_number=phone_number,
            amount=amount,
            account_reference=reference,
            # transaction_desc=description
        )
        
        if stk_push_response.get('success'):
            # Store checkout request ID in session for later verification
            request.session['checkout_request_id'] = stk_push_response.get('checkout_request_id')
            request.session['payment_id'] = payment.id
            
            messages.success(request, "Payment request sent to your phone. Please complete the payment.")
            return redirect('payment_processing')
        else:
            payment.status = 'failed'
            payment.save()
            messages.error(request, f"Failed to initiate payment: {stk_push_response.get('message')}")
            return redirect('health_provider_page')
    
    return redirect('health_provider_page')

@login_required(login_url='/auth/login/')
def payment_processing(request):
    payment_id = request.session.get('payment_id')
    checkout_request_id = request.session.get('checkout_request_id')
    
    if not payment_id or not checkout_request_id:
        messages.error(request, "Invalid payment session.")
        return redirect('health_provider_page')
    
    payment = get_object_or_404(Payment, id=payment_id)
    
    return render(request, 'payment_processing.html', {
        'payment': payment,
        'checkout_request_id': checkout_request_id
    })
@login_required(login_url='/auth/login/')
def check_payment_status(request):
    try:
        checkout_request_id = request.session.get('checkout_request_id')
        payment_id = request.session.get('payment_id')

        if not checkout_request_id or not payment_id:
            return JsonResponse({'success': False, 'message': 'Invalid payment session'})

        payment = get_object_or_404(Payment, id=payment_id)

        # Check payment status with M-Pesa
        status_response = mpesa_api.check_payment_status(checkout_request_id)

        if status_response.get('success'):
            result = status_response.get('result')
            result_code = result.get('ResultCode')

            if result_code == 0:
                # Payment successful
                payment.status = 'completed'
                payment.transaction_id = result.get('MpesaReceiptNumber', '')
                payment.save()

                # Create the relevant service based on payment_for
                if payment.payment_for == 'appointment':
                    # Create appointment
                    appointment = Appointment.objects.create(
                        user=request.user,
                        health_provider=payment.health_provider,
                        date_time=request.session.get('appointment_date_time'),
                        reason=request.session.get('appointment_reason'),
                        status='Pending'
                    )

                    logger.info(f"Appointment created: {appointment.id}")

                    # Clear session data
                    request.session.pop('appointment_date_time', None)
                    request.session.pop('appointment_reason', None)

                    return JsonResponse({
                        'success': True,
                        'message': 'Payment successful. Appointment created.',
                        'redirect_url': reverse('appointment_confirmation')
                    })
                else:  # consultation
                    # Create consultation
                    Consultation.objects.create(
                        user=request.user,
                        health_provider=payment.health_provider,
                        issue=request.session.get('consultation_issue'),
                        status='Pending'
                    )

                    # Clear session data
                    request.session.pop('consultation_issue', None)

                    return JsonResponse({
                        'success': True,
                        'message': 'Payment successful. Consultation request sent.',
                        'redirect_url': reverse('consultation_confirmation')
                    })
            else:
                # Payment failed or pending
                message = result.get('ResultDesc', 'Payment verification failed')
                return JsonResponse({'success': False, 'message': message})
        else:
            return JsonResponse({'success': False, 'message': status_response.get('message')})

    except Exception as e:
        logger.error(f"Error checking payment status: {str(e)}")
        return JsonResponse({'success': False, 'message': 'An error occurred while checking payment status.'})

@csrf_exempt
def mpesa_callback(request):
    if request.method == 'POST':
        try:
            # 1. Parse the callback data
            data = json.loads(request.body)
            callback = data.get('Body', {}).get('stkCallback', {})
            result_code = callback.get('ResultCode')
            
            # 2. Extract metadata safely
            metadata = {}
            for item in callback.get('CallbackMetadata', {}).get('Item', []):
                name = item.get('Name')
                value = item.get('Value')
                if name and value is not None:
                    metadata[name] = value
            
            # 3. Get the payment reference
            reference = metadata.get('AccountReference')
            if not reference:
                logger.error("Missing AccountReference in callback")
                return JsonResponse({'ResultCode': 1, 'ResultDesc': 'Missing reference'}, status=400)
            
            # 4. Find and update the payment
            try:
                payment = Payment.objects.get(reference=reference)
                
                if result_code == 0:
                    # Successful payment
                    payment.status = 'completed'
                    payment.transaction_id = metadata.get('MpesaReceiptNumber')
                    # Ensure phone number follows 254 format
                    phone = metadata.get('PhoneNumber', '')
                    payment.phone_number = f"254{phone[-9:]}" if phone else payment.phone_number
                    payment.save()
                    logger.info(f"Payment {reference} marked as completed. Receipt: {payment.transaction_id}")
                else:
                    # Failed payment
                    payment.status = 'failed'
                    payment.save()
                    logger.warning(f"Payment {reference} failed. ResultCode: {result_code}")
                
                return JsonResponse({'ResultCode': 0, 'ResultDesc': 'Success'})
                
            except Payment.DoesNotExist:
                logger.error(f"Payment not found for reference: {reference}")
                return JsonResponse({'ResultCode': 1, 'ResultDesc': 'Payment not found'}, status=404)
                
        except json.JSONDecodeError:
            logger.error("Invalid JSON in callback")
            return JsonResponse({'ResultCode': 1, 'ResultDesc': 'Invalid JSON'}, status=400)
            
        except Exception as e:
            logger.error(f"Callback processing error: {str(e)}", exc_info=True)
            return JsonResponse({'ResultCode': 1, 'ResultDesc': 'Processing error'}, status=500)
    
    return JsonResponse({'ResultCode': 1, 'ResultDesc': 'Invalid method'}, status=405)
    

# views.py - Add this at the top with your other imports
# views.py (replace existing functions with these)

@login_required(login_url='/auth/login/') # Ensure user is logged in
def create_consultation(request, provider_id):
    """
    Handles the creation of a consultation request via standard form POST.
    Sends email confirmation and redirects to a confirmation page.
    """
    # Get the provider object or return 404 if not found
    provider = get_object_or_404(HealthProvider, id=provider_id)

    if request.method == 'POST':
        # Get data from the submitted form
        issue = request.POST.get('issue', '').strip()
        # Get email from the hidden input field populated by JS
        user_email = request.POST.get('user_email', '').strip()
        # Check which button was clicked ('request_only' or 'pay_now')
        action = request.POST.get('action')

        # --- Basic Validation ---
        if not issue:
            messages.error(request, "Please describe your issue.")
            # Redirect back to the provider list page
            # You might want to redirect back to the specific provider's details
            # if you have such a page, or handle showing the form with errors.
            return redirect('health_provider_page')
        if not user_email:
             messages.error(request, "Please provide your email address.")
             return redirect('health_provider_page')
        # You could add more validation here (e.g., email format)

        # --- Create Consultation Object ---
        try:
            consultation = Consultation.objects.create(
                user=request.user,
                health_provider=provider,
                issue=issue,
                status='Requested' # Initial status
                # Consider setting status based on 'action' if payment flow is complex
                # e.g., status='Pending Payment' if action == 'pay_now'
            )
        except Exception as e:
             logger.error(f"Error creating consultation object: {str(e)}")
             messages.error(request, "An error occurred while saving your request. Please try again.")
             return redirect('health_provider_page')

        # --- Send Confirmation Email ---
        try:
            # Render the HTML email content from a template
            html_message = render_to_string('emails/consultation_requested.html', {
                'user': request.user,
                'consultation': consultation,
                'provider': provider
            })
            # Send the email
            send_mail(
                subject=f'Consultation Request Received - ID: #{consultation.id}',
                message=f'Your consultation request with {provider.name} regarding "{issue[:50]}..." has been received. Request ID: #{consultation.id}.', # Plain text fallback
                from_email=settings.DEFAULT_FROM_EMAIL, # Email from settings.py
                recipient_list=[user_email], # Send to the email provided in the form
                fail_silently=False, # Raise an exception if sending fails
                html_message=html_message # Attach the HTML version
            )
            # Mark email as sent (optional, if your model has this field)
            # consultation.email_sent = True
            # consultation.save()
            # Add success message for the user
            messages.success(request, f"Consultation request #{consultation.id} sent successfully! Please check your email ({user_email}) for confirmation.")

        except Exception as e:
            # Log the email error and inform the user, but don't stop the process
            logger.error(f"Consultation Email failed for request {consultation.id} to {user_email}: {str(e)}")
            messages.warning(request, f"Consultation request #{consultation.id} was received, but the confirmation email could not be sent. Please contact support if you don't hear back.")

        # --- Redirect based on Action ---
        if action == 'pay_now':
            # If 'Pay Now' was clicked, you might redirect to a payment initiation page.
            # For now, we'll just redirect to the standard confirmation page.
            # You'll need to implement the payment flow separately.
            # Example for future: return redirect('initiate_payment_for_consultation', consultation_id=consultation.id)
            messages.info(request, "Your request is saved. You can proceed with payment if required.") # Optional message for payment context
            return redirect('consultation_confirmation') # Redirect to confirmation page
        else:
            # If 'Request Only' was clicked, redirect straight to the confirmation page
            return redirect('consultation_confirmation') # Name of the URL pattern for the confirmation page

    else:
        # If the request method is not POST (e.g., GET), just redirect back
        # Or you could render a form page if appropriate
        messages.error(request, "Invalid request method.")
        return redirect('health_provider_page')


@login_required(login_url='/auth/login/') # Ensure user is logged in
def create_appointment(request, provider_id):
    """
    Handles the creation of an appointment request via standard form POST.
    Sends email confirmation and redirects to a confirmation page.
    """
    # Get the provider object or return 404 if not found
    provider = get_object_or_404(HealthProvider, id=provider_id)

    if request.method == 'POST':
        # Get data from the submitted form
        date_time = request.POST.get('date_time')
        reason = request.POST.get('reason', '').strip()
        # Get email from the hidden input field populated by JS
        user_email = request.POST.get('user_email', '').strip()
        # Check which button was clicked ('request_only' or 'pay_now')
        action = request.POST.get('action')

        # --- Basic Validation ---
        if not date_time:
            messages.error(request, "Please select a date and time for the appointment.")
            return redirect('health_provider_page')
        if not user_email:
            messages.error(request, "Please provide your email address.")
            return redirect('health_provider_page')
        # You could add validation for date format, ensure date is in the future, etc.

        # --- Create Appointment Object ---
        try:
            appointment = Appointment.objects.create(
                user=request.user,
                health_provider=provider,
                date_time=date_time,
                reason=reason,
                status='Requested' # Initial status
                # Consider setting status based on 'action' if payment flow is complex
            )
        except Exception as e:
             logger.error(f"Error creating appointment object: {str(e)}")
             messages.error(request, "An error occurred while saving your appointment request. Please try again.")
             return redirect('health_provider_page')

        # --- Send Confirmation Email ---
        try:
            # Render the HTML email content from a template
            html_message = render_to_string('emails/appointment_requested.html', {
                'user': request.user,
                'appointment': appointment,
                'provider': provider
            })
            # Send the email
            send_mail(
                subject=f'Appointment Request Received - ID: #{appointment.id}',
                message=f'Your appointment request with {provider.name} for {appointment.date_time} has been received. Request ID: #{appointment.id}.', # Plain text fallback
                from_email=settings.DEFAULT_FROM_EMAIL, # Email from settings.py
                recipient_list=[user_email], # Send to the email provided in the form
                fail_silently=False, # Raise an exception if sending fails
                html_message=html_message # Attach the HTML version
            )
            # Mark email as sent (optional)
            # appointment.email_sent = True
            # appointment.save()
            # Add success message for the user
            messages.success(request, f"Appointment request #{appointment.id} sent successfully! Please check your email ({user_email}) for confirmation.")

        except Exception as e:
            # Log the email error and inform the user, but don't stop the process
            logger.error(f"Appointment Email failed for request {appointment.id} to {user_email}: {str(e)}")
            messages.warning(request, f"Appointment request #{appointment.id} was received, but the confirmation email could not be sent. Please contact support if you don't hear back.")

        # --- Redirect based on Action ---
        if action == 'pay_now':
            # If 'Pay Now' was clicked, you might redirect to a payment initiation page.
            # For now, we'll just redirect to the standard confirmation page.
            # Example for future: return redirect('initiate_payment_for_appointment', appointment_id=appointment.id)
            messages.info(request, "Your request is saved. You can proceed with payment if required.") # Optional message for payment context
            return redirect('appointment_confirmation') # Redirect to confirmation page
        else:
            # If 'Book Appointment' was clicked, redirect straight to the confirmation page
            return redirect('appointment_confirmation') # Name of the URL pattern for the confirmation page

    else:
        # If the request method is not POST (e.g., GET), just redirect back
        messages.error(request, "Invalid request method.")
        return redirect('health_provider_page')

# --- Remember to have these simple views to render the confirmation pages ---

@login_required(login_url='/auth/login/')
def consultation_confirmation(request):
    # Renders templates/consultation_confirmation.html
    return render(request, 'consultation_confirmation.html')

@login_required(login_url='/auth/login/')
def appointment_confirmation(request):
    # Renders templates/appointment_confirmation.html
    return render(request, 'appointment_confirmation.html')
 
@login_required(login_url='/auth/login/')
def send_message(request, consultation_id=None, appointment_id=None):
    if request.method == 'POST':
        message_text = request.POST.get('message')
        receiver_id = request.POST.get('receiver_id')
        
        if not message_text or not receiver_id:
            messages.error(request, "Missing required fields.")
            return redirect('health_provider_dashboard')
        
        receiver = get_object_or_404(User, id=receiver_id)
        
        Message.objects.create(
            sender=request.user,
            receiver=receiver,
            consultation_id=consultation_id,
            appointment_id=appointment_id,
            message=message_text
        )
        
        messages.success(request, "Message sent successfully!")
        return redirect('health_provider_dashboard')
    
    return redirect('health_provider_dashboard')


@login_required(login_url='/auth/login/')
def view_messages(request):
    messages_received = Message.objects.filter(receiver=request.user).order_by('-timestamp')
    return render(request, 'view_messages.html', {'messages_received': messages_received})


@login_required(login_url='/auth/login/')
def health_provider_dashboard(request):
    # Assuming the logged-in user is a health provider
    health_provider = HealthProvider.objects.get(user=request.user)
    
    # Fetch pending consultation requests for the health provider
    consultation_requests = Consultation.objects.filter(health_provider=health_provider, status='Pending')
    
    # Render the dashboard template with the consultation requests
    return render(request, 'health_provider_dashboard.html', {
        'consultation_requests': consultation_requests
    })
    
    
@login_required(login_url='/auth/login/')
def initiate_service_payment(request, service_type, service_id):
    """Separate payment initiation for existing services"""
    if service_type == 'consultation':
        service = get_object_or_404(Consultation, id=service_id, user=request.user)
        amount = 1  # Consultation fee
    else:
        service = get_object_or_404(Appointment, id=service_id, user=request.user)
        amount = 1  # Appointment fee
    
    if request.method == 'POST':
        phone = request.POST.get('phone')
        
        # Generate unique reference
        ref = f"{service_type.upper()}_{service.id}"
        
        # Initiate payment
        response = mpesa_api.initiate_stk_push(
            phone_number=phone,
            amount=amount,
            account_reference=ref
        )
        
        if response['success']:
            # Create payment record
            Payment.objects.create(
                user=request.user,
                health_provider=service.health_provider,
                amount=amount,
                reference=ref,
                payment_for=service_type,
                phone_number=phone,
                status='pending'
            )
            
            # Update service record
            service.payment_reference = ref
            service.save()
            
            return render(request, 'payment_processing.html', {
                'checkout_id': response['checkout_request_id'],
                'service_type': service_type,
                'service_id': service_id
            })
    
    return render(request, 'initiate_payment.html', {
        'service': service,
        'service_type': service_type,
        'amount': amount
    })
