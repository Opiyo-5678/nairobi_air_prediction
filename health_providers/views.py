from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from datetime import datetime, timedelta
from .models import HealthProvider, Consultation, Appointment, Payment, Message
# from .mpesa import MpesaAPI
import uuid
import json
import logging
from django.db.models import Q
from django.utils import timezone
from weasyprint import HTML, CSS
from django.template.loader import get_template
from io import BytesIO
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Payment
from .forms import PaymentForm  # Create this form
from health_providers.mpesa import MpesaAccessToken, LipanaMpesaPpassword
import json
import requests
from django.http import HttpResponse
from django.shortcuts import render, redirect
from requests.auth import HTTPBasicAuth
from rest_framework import generics
from .serializers import HealthProviderSerializer

logger = logging.getLogger(__name__)

# Initialize M-Pesa API with your credentials

# mpesa_api = MpesaAPI()
#     consumer_key="p6K0xADABjX4RcZkeJMSOhGGTLeNZx1NWZ3dKM0xw32FJGpp",
#     consumer_secret="QuH0qNG7WtI78maGF8W3QYSuqgEKWSGvTgmaHxAL2v7XRmMAY3mDvrAckwDA7K0Z",
#     business_shortcode="174379",
#     passkey="bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919",
#     callback_url="https://mydomain.com/path",  # Make sure to update this with your actual callback URL
#     environment="sandbox"  # Use "production" for live environment
# )

# Health Provider Views
def health_provider_page(request):
    health_providers = HealthProvider.objects.all()
    return render(request, 'health_provider.html', {'health_providers': health_providers})

@login_required(login_url='/auth/login/')
def health_provider_dashboard(request):
    provider = get_object_or_404(HealthProvider, user=request.user)
    appointments = Appointment.objects.filter(health_provider=provider)
    consultations = Consultation.objects.filter(health_provider=provider)
    
    return render(request, 'health_provider_dashboard.html', {
        'provider': provider,
        'appointments': appointments,
        'consultations': consultations
    })
    
# Updated confirmation views to show receipt information
def appointment_confirmation(request):
    """Display appointment confirmation page"""
    payment_id = request.session.get('last_payment_id')
    appointment_id = request.session.get('last_appointment_id')
    
    context = {}
    if payment_id:
        try:
            payment = Payment.objects.get(id=payment_id)
            context['payment'] = payment
        except Payment.DoesNotExist:
            pass
            
    if appointment_id:
        try:
            appointment = Appointment.objects.get(id=appointment_id)
            context['appointment'] = appointment
        except Appointment.DoesNotExist:
            pass
            
    return render(request, 'appointment_confirmation.html', context)

def consultation_confirmation(request):
    """Display consultation confirmation page"""
    payment_id = request.session.get('last_payment_id')
    consultation_id = request.session.get('last_consultation_id')
    
    context = {}
    if payment_id:
        try:
            payment = Payment.objects.get(id=payment_id)
            context['payment'] = payment
        except Payment.DoesNotExist:
            pass
            
    if consultation_id:
        try:
            consultation = Consultation.objects.get(id=consultation_id)
            context['consultation'] = consultation
        except Consultation.DoesNotExist:
            pass
            
    return render(request, 'consultation_confirmation.html', context)

@login_required(login_url='/auth/login/')
def view_messages(request):
    """Display all messages for the current user"""
    messages_received = Message.objects.filter(receiver=request.user)
    messages_sent = Message.objects.filter(sender=request.user)
    return render(request, 'view_messages.html', {
        'messages_received': messages_received,
        'messages_sent': messages_sent
    })

# Updated Service Creation Views to capture client name and email
def create_consultation(request, provider_id):
    provider = get_object_or_404(HealthProvider, id=provider_id)
    
    if request.method == 'POST':
        issue = request.POST.get('issue')
        client_name = request.POST.get('client_name')
        client_email = request.POST.get('client_email')
        
        if not issue:
            messages.error(request, "Please describe your issue.")
            return render(request, 'create_consultation.html', {'provider': provider})
            
        if not client_name or not client_email:
            messages.error(request, "Please provide your name and email.")
            return render(request, 'create_consultation.html', {'provider': provider})
        
        # Store in session with expiration
        request.session['consultation_details'] = {
            'issue': issue,
            'client_name': client_name,
            'client_email': client_email,
            'provider_id': provider_id,
            'created_at': datetime.now().isoformat()
        }
        request.session.modified = True
        
        return render(request, 'pay.html', {
            'provider': provider,
            'payment_for': 'consultation',
            'amount': 500  # Consultation fee
        })
    
    return render(request, 'create_consultation.html', {'provider': provider})

def create_appointment(request, provider_id):
    provider = get_object_or_404(HealthProvider, id=provider_id)
    
    if request.method == 'POST':
        date_time_str = request.POST.get('date_time')
        reason = request.POST.get('reason')
        client_name = request.POST.get('client_name')
        client_email = request.POST.get('client_email')
        
        if not date_time_str:
            messages.error(request, "Please select a date and time.")
            return render(request, 'create_appointment.html', {'provider': provider})
            
        if not client_name or not client_email:
            messages.error(request, "Please provide your name and email.")
            return render(request, 'create_appointment.html', {'provider': provider})
        
        # Store in session with expiration
        request.session['appointment_details'] = {
            'date_time': date_time_str,
            'reason': reason,
            'client_name': client_name,
            'client_email': client_email,
            'provider_id': provider_id,
            'created_at': datetime.now().isoformat()
        }
        request.session.modified = True
        
        return render(request, 'payment_processing.html', {
            'provider': provider,
            'payment_for': 'appointment',
            'amount': 1000  # Appointment fee
        })
    
    return render(request, 'create_appointment.html', {'provider': provider})

# # Updated to store phone number with payment
# @login_required
# def initiate_payment(request):
#     if request.method == 'POST':
#         try:
#             # Parse JSON data if it's an AJAX request
#             if request.headers.get('Content-Type') == 'application/json':
#                 data = json.loads(request.body)
#                 phone = data.get('phone_number')
#                 amount = data.get('amount', '1')
#                 payment_for = data.get('payment_for', 'service')
#             else:
#                 # Get form data
#                 phone = request.POST.get('phone_number')
#                 amount = request.POST.get('amount', '1')
#                 payment_for = request.POST.get('payment_for', 'service')
            
#             if not phone:
#                 return JsonResponse({'success': False, 'message': 'Phone number is required'}, status=400)
            
#             # Format phone number
#             try:
#                 phone = mpesa_api.format_phone_number(phone)
#             except ValueError as e:
#                 return JsonResponse({'success': False, 'message': str(e)}, status=400)
            
#             # Generate unique reference
#             reference = f"HEALTH-{uuid.uuid4().hex[:6].upper()}"
            
#             # Get provider ID from session
#             if payment_for == 'appointment':
#                 provider_id = request.session.get('appointment_details', {}).get('provider_id')
#             elif payment_for == 'consultation':
#                 provider_id = request.session.get('consultation_details', {}).get('provider_id')
#             else:
#                 provider_id = None
                
#             if not provider_id:
#                 return JsonResponse({'success': False, 'message': 'Service provider not found'}, status=400)
                
#             try:
#                 provider = HealthProvider.objects.get(id=provider_id)
#             except HealthProvider.DoesNotExist:
#                 return JsonResponse({'success': False, 'message': 'Provider not found'}, status=404)
            
#             # Initiate payment
#             response = mpesa_api.initiate_stk_push(
#                 phone_number=phone,
#                 amount=amount,
#                 account_reference=reference
#             )
            
#             if response['success']:
#                 # Create payment record
#                 payment = Payment.objects.create(
#                     user=request.user,
#                     health_provider=provider,
#                     amount=amount,
#                     reference=reference,
#                     payment_for=payment_for,
#                     phone_number=phone,
#                     status='pending'
#                 )
                
#                 # Store payment info in session
#                 request.session['payment_session'] = {
#                     'payment_id': payment.id,
#                     'checkout_request_id': response['checkout_request_id'],
#                     'merchant_request_id': response['merchant_request_id'],
#                     'created_at': datetime.now().isoformat()
#                 }
#                 request.session.modified = True
                
#                 return JsonResponse({
#                     'success': True,
#                     'message': 'Payment request sent. Check your phone.',
#                     'checkout_request_id': response['checkout_request_id']
#                 })
#             else:
#                 return JsonResponse({
#                     'success': False, 
#                     'message': response.get('error', 'Failed to initiate payment')
#                 }, status=400)
                
#         except Exception as e:
#             logger.error(f"Payment initiation error: {str(e)}", exc_info=True)
#             return JsonResponse({
#                 'success': False,
#                 'message': f"Error processing request: {str(e)}"
#             }, status=500)
            
#     return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=405)

# # @login_required(login_url='/auth/login/')
# # def payment_processing(request):
# #     session_data = request.session.get('payment_session')
    
# #     if not session_data:
# #         messages.error(request, "Invalid payment session.")
# #         return redirect('health_provider_page')
    
# #     # Check if session is expired
# #     created_at = datetime.fromisoformat(session_data['created_at'])
# #     if datetime.now() - created_at > timedelta(minutes=30):
# #         messages.error(request, "Payment session expired.")
# #         return redirect('health_provider_page')
    
# #     try:
# #         payment = Payment.objects.get(
# #             id=session_data['payment_id'],
# #             user=request.user,
# #             status='pending'
# #         )
# #     except Payment.DoesNotExist:
# #         messages.error(request, "Invalid payment session.")
# #         return redirect('health_provider_page')
    
# #     return render(request, 'payment_processing.html', {
# #         'payment': payment,
# #         'checkout_request_id': session_data['checkout_request_id']
# #     })

# # New view to manually confirm payment with transaction ID
@login_required(login_url='/auth/login/')
def confirm_payment(request):
    if request.method == 'POST':
        transaction_id = request.POST.get('transaction_id')
        session_data = request.session.get('payment_session')
        
        if not session_data:
            messages.error(request, "Payment session expired or invalid.")
            return redirect('health_provider_page')
            
        if not transaction_id:
            messages.error(request, "Transaction ID is required.")
            return redirect('pay.html')
            
        try:
            payment = Payment.objects.get(id=session_data['payment_id'])
            
            # Update payment status
            payment.status = 'completed'
            payment.transaction_id = transaction_id
            payment.confirmed_at = timezone.now()
            payment.save()
            
            # Process the payment
            result = handle_successful_payment(request, payment)
            
            if isinstance(result, JsonResponse):
                data = json.loads(result.content)
                if data.get('success'):
                    messages.success(request, data.get('message', 'Payment confirmed successfully.'))
                    return redirect(data.get('redirect_url', 'health_provider_page'))
                else:
                    messages.error(request, data.get('message', 'Error processing payment.'))
            
            return redirect('health_provider_page')
            
        except Payment.DoesNotExist:
            messages.error(request, "Payment record not found.")
            return redirect('health_provider_page')
        
    return redirect('payment_processing.html')

@login_required(login_url='/auth/login/')
def check_payment_status(request):
    session_data = request.session.get('payment_session')
    if not session_data:
        return JsonResponse({
            'success': False,
            'message': 'Payment session expired or invalid'
        }, status=400)
        
    # Check if session is expired (30 minutes)
    created_at = datetime.fromisoformat(session_data['created_at'])
    if datetime.now() - created_at > timedelta(minutes=30):
        return JsonResponse({
            'success': False,
            'message': 'Payment session expired'
        }, status=400)
    
    try:
        payment = Payment.objects.get(id=session_data['payment_id'])
        
        # If payment is already completed
        if payment.status == 'completed':
            return handle_successful_payment(request, payment)
        
        # Else check with M-Pesa API
        checkout_request_id = session_data['checkout_request_id']
        status_response = mpesa_api.verify_payment(checkout_request_id)
        
        if status_response['success']:
            if status_response.get('status') == 'completed':
                # Update payment record
                payment.status = 'completed'
                payment.transaction_id = status_response.get('mpesa_receipt', '')
                payment.confirmed_at = timezone.now()
                payment.save()
                
                # Handle post-payment actions
                return handle_successful_payment(request, payment)
            else:
                # Still pending
                return JsonResponse({
                    'success': False,
                    'message': status_response.get('result_desc', 'Payment is still processing')
                })
        else:
            # Error checking status
            logger.error(f"Payment status check error: {status_response.get('error')}")
            return JsonResponse({
                'success': False,
                'message': 'Failed to verify payment status. Please try again.'
            })
            
    except Payment.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Payment record not found'
        }, status=404)
    except Exception as e:
        logger.error(f"Payment status check exception: {str(e)}", exc_info=True)
        return JsonResponse({
            'success': False,
            'message': f"Error checking payment status: {str(e)}"
        }, status=500)
        
# Updated to include client name and email
def handle_successful_payment(request, payment):
    """Handle post-payment actions for both appointment and consultation"""
    if payment.payment_for == 'appointment':
        details = request.session.get('appointment_details')
        if not details:
            return JsonResponse({
                'success': False,
                'message': 'Appointment details missing',
                'redirect_url': reverse('health_provider_page')
            })
        
        try:
            date_time = datetime.strptime(details['date_time'], '%Y-%m-%dT%H:%M')
        except ValueError:
            return JsonResponse({
                'success': False,
                'message': 'Invalid date format',
                'redirect_url': reverse('health_provider_page')
            })
        
        # Create appointment with client name and email
        appointment = Appointment.objects.create(
            user=request.user,
            health_provider=payment.health_provider,
            date_time=date_time,
            reason=details['reason'],
            client_name=details.get('client_name', ''),
            client_email=details.get('client_email', ''),
            status='Pending',
            is_paid=True,
            payment_reference=payment.reference
        )
        
        # Store appointment ID for confirmation page
        request.session['last_appointment_id'] = appointment.id
        request.session['last_payment_id'] = payment.id
        
        # Send email to both user and provider
        send_confirmation_email(
            user=request.user,
            payment_type='appointment',
            provider_name=payment.health_provider.name,
            details={
                'date_time': date_time,
                'reason': details['reason'],
                'client_name': details.get('client_name', ''),
                'client_email': details.get('client_email', ''),
                'payment_reference': payment.reference,
                'transaction_id': payment.transaction_id,
                'receipt_number': payment.receipt_number
            }
        )
        
        # Clear session data
        request.session.pop('appointment_details', None)
        request.session.pop('payment_session', None)
        
        return JsonResponse({
            'success': True,
            'message': 'Appointment booked successfully',
            'redirect_url': reverse('appointment_confirmation')
        })
        
    else:  # consultation
        details = request.session.get('consultation_details')
        if not details:
            return JsonResponse({
                'success': False,
                'message': 'Consultation details missing',
                'redirect_url': reverse('health_provider_page')
            })
        
        # Create consultation with client name and email
        consultation = Consultation.objects.create(
            user=request.user,
            health_provider=payment.health_provider,
            issue=details['issue'],
            client_name=details.get('client_name', ''),
            client_email=details.get('client_email', ''),
            status='Pending',
            is_paid=True,
            payment_reference=payment.reference
        )
        
        # Store consultation ID for confirmation page
        request.session['last_consultation_id'] = consultation.id
        request.session['last_payment_id'] = payment.id
        
        # Send email to both user and provider
        send_confirmation_email(
            user=request.user,
            payment_type='consultation',
            provider_name=payment.health_provider.name,
            details={
                'issue': details['issue'],
                'client_name': details.get('client_name', ''),
                'client_email': details.get('client_email', ''),
                'payment_reference': payment.reference,
                'transaction_id': payment.transaction_id,
                'receipt_number': payment.receipt_number
            }
        )
        
        # Clear session data
        request.session.pop('consultation_details', None)
        request.session.pop('payment_session', None)
        
        return JsonResponse({
            'success': True,
            'message': 'Consultation requested successfully',
            'redirect_url': reverse('consultation_confirmation')
        })

# Enhanced email function for better email confirmation
def send_confirmation_email(user, payment_type, provider_name, details):
    subject = f'Your {payment_type.title()} Confirmation'
    
    # Create email content based on payment type
    if payment_type == 'appointment':
        html_message = render_to_string('email/appointment_confirmation.html', {
            'user': user,
            'provider_name': provider_name,
            'date_time': details.get('date_time'),
            'reason': details.get('reason'),
            'client_name': details.get('client_name'),
            'client_email': details.get('client_email'),
            'payment_reference': details.get('payment_reference'),
            'transaction_id': details.get('transaction_id'),
            'receipt_number': details.get('receipt_number')
        })
    else:  # consultation
        html_message = render_to_string('email/consultation_confirmation.html', {
            'user': user,
            'provider_name': provider_name,
            'issue': details.get('issue'),
            'client_name': details.get('client_name'),
            'client_email': details.get('client_email'),
            'payment_reference': details.get('payment_reference'),
            'transaction_id': details.get('transaction_id'),
            'receipt_number': details.get('receipt_number')
        })
    
    plain_message = strip_tags(html_message)
    from_email = 'austineopiyo84@gmail.com'  # Update with your email
    
    # Send to user
    to_email = user.email
    send_mail(subject, plain_message, from_email, [to_email], html_message=html_message)
    
    # If guest email is different from user email, send there too
    guest_email = details.get('client_email')
    if guest_email and guest_email != user.email:
        send_mail(subject, plain_message, from_email, [guest_email], html_message=html_message)
    
    # Also send notification to the health provider
    if payment_type == 'appointment':
        provider_subject = f'New Appointment Booking'
    else:
        provider_subject = f'New Consultation Request'
        
    # You would need to create these templates
    provider_html_message = render_to_string(f'email/provider_{payment_type}_notification.html', {
        'client_name': details.get('client_name'),
        'client_email': details.get('client_email')
    })
    
    provider_plain_message = strip_tags(provider_html_message)
    try:
        provider = HealthProvider.objects.get(name=provider_name)
        provider_email = provider.email
        send_mail(provider_subject, provider_plain_message, from_email, [provider_email], html_message=provider_html_message)
    except HealthProvider.DoesNotExist:
        logger.error(f"Could not find provider with name: {provider_name}")

@login_required(login_url='/auth/login/')
def send_message(request, consultation_id=None, appointment_id=None):
    if request.method == 'POST':
        message_text = request.POST.get('message')
        
        if consultation_id:
            consultation = get_object_or_404(Consultation, id=consultation_id)
            # Determine sender and receiver
            if request.user == consultation.user:
                sender = request.user
                receiver = consultation.health_provider.user
            else:
                sender = request.user
                receiver = consultation.user
            
            Message.objects.create(
                sender=sender,
                receiver=receiver,
                consultation=consultation,
                message=message_text
            )
            return redirect('view_messages')
            
        elif appointment_id:
            appointment = get_object_or_404(Appointment, id=appointment_id)
            # Determine sender and receiver
            if request.user == appointment.user:
                sender = request.user
                receiver = appointment.health_provider.user
            else:
                sender = request.user
                receiver = appointment.user
            
            Message.objects.create(
                sender=sender,
                receiver=receiver,
                appointment=appointment,
                message=message_text
            )
            return redirect('view_messages')
    
    return redirect('health_provider_page')

# API View remains unchanged



class HealthProviderList(generics.ListAPIView):
    queryset = HealthProvider.objects.all()
    serializer_class = HealthProviderSerializer
    
@login_required
def payment_history(request):
    payments = Payment.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'payment_history.html', {'payments': payments})


@login_required
def make_payment(request):
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            try:
                # Create payment object but don't save yet
                payment = form.save(commit=False)
                payment.user = request.user
                
                # Set required fields not in the form
                payment.reference = f"PAY-{uuid.uuid4().hex[:8].upper()}"
                payment.status = 'pending'  # Initial status
                
                # Get health provider - adjust this based on your logic
                # Example: if user selects provider in form or has one assigned
                health_provider_id = request.POST.get('health_provider_id')
                if health_provider_id:
                    payment.health_provider = HealthProvider.objects.get(id=health_provider_id)
                else:
                    raise ValueError("Health provider is required")
                
                # Save to get an ID before STK Push
                payment.save()
                
                # Initiate M-Pesa STK Push
                stk_response = initiate_mpesa_stk_push(
                    phone_number=payment.phone_number,
                    amount=str(payment.amount),
                    account_reference=payment.reference
                )
                
                if stk_response.get('ResponseCode') == '0':
                    payment.transaction_id = stk_response.get('CheckoutRequestID')
                    payment.save()
                    messages.success(request, "Payment initiated! Check your phone to complete")
                    return redirect('payment_history')
                else:
                    payment.status = 'failed'
                    payment.save()
                    messages.error(request, f"Payment failed: {stk_response.get('ResponseDescription')}")
                    
            except Exception as e:
                messages.error(request, f"Error processing payment: {str(e)}")
        else:
            messages.error(request, "Invalid form data. Please check your inputs.")
            # Print form errors for debugging
            print(form.errors)
    else:
        form = PaymentForm()
    
    # Get providers for dropdown if needed
    providers = HealthProvider.objects.all()
    return render(request, 'make_payment.html', {
        'form': form,
        'providers': providers
    })


def token(request):
    consumer_key = '1ktP51i1jECFDDd8UdimELCE2cAZyjO4Uz6ufF5GDbpohIpd'
    consumer_secret = 'qUbtwAnveOESfoJ7M8sj0CbeQww6TmvpzMcoWiQm5iGwlKPGrF65MlZ65dmuZ5f1'
    api_URL = 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'

    r = requests.get(api_URL, auth=HTTPBasicAuth(
        consumer_key, consumer_secret))
    mpesa_access_token = json.loads(r.text)
    validated_mpesa_access_token = mpesa_access_token["access_token"]

    return render(request, 'token.html', {"token":validated_mpesa_access_token})


def pay(request):
    return render(request, 'pay.html')



def stk(request):
    if request.method =="POST":
        phone = request.POST['phone']
        amount = request.POST['amount']
        access_token = MpesaAccessToken.validated_mpesa_access_token
        api_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
        headers = {"Authorization": "Bearer %s" % access_token}
        request = {
            "BusinessShortCode": LipanaMpesaPpassword.Business_short_code,
            "Password": LipanaMpesaPpassword.decode_password,
            "Timestamp": LipanaMpesaPpassword.lipa_time,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": amount,
            "PartyA": phone,
            "PartyB": LipanaMpesaPpassword.Business_short_code,
            "PhoneNumber": phone,
            "CallBackURL": "https://sandbox.safaricom.co.ke/mpesa/",
            "AccountReference": "PrimCare",
            "TransactionDesc": "Web Development Charges"
        }
        response = requests.post(api_url, json=request, headers=headers)
        return HttpResponse("Success")