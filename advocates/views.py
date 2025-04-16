from django.shortcuts import render, redirect, get_object_or_404
from django.core.mail import send_mail, EmailMessage
from django.conf import settings
from django.contrib import messages
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.utils import timezone
from datetime import datetime
import requests
import json
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from io import BytesIO
from django.http import Http404

import base64
from .models import CleanAirWarrior, ConsultationRequest, Appointment, Donation
from .forms import ConsultationForm, AppointmentForm, DonationForm
#from .mpesa import MpesaGateway  # Import the MpesaGateway class
from requests.auth import HTTPBasicAuth
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from .mpesa import MpesaAccessToken, LipanaMpesaPpassword
from django.shortcuts import get_object_or_404
# ============ M-Pesa Helper Functions ============

def get_mpesa_token():
    """Helper function to get M-Pesa access token"""
    api_url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    response = requests.get(
        api_url,
        auth=HTTPBasicAuth(settings.MPESA_CONSUMER_KEY, settings.MPESA_CONSUMER_SECRET)
    )
    return json.loads(response.text).get('access_token')

def generate_mpesa_password():
    """Generate Lipa Na M-Pesa password"""
    lipa_time = datetime.now().strftime('%Y%m%d%H%M%S')
    data_to_encode = settings.MPESA_BUSINESS_SHORTCODE + settings.MPESA_PASSKEY + lipa_time
    online_password = base64.b64encode(data_to_encode.encode())
    return online_password.decode('utf-8'), lipa_time

@login_required
def initiate_donation(request):
    if request.method == 'POST':
        form = DonationForm(request.POST)
        if form.is_valid():
            donation = form.save(commit=False)
            donation.user = request.user
            
            try:
                # Initialize M-Pesa classes
                mpesa_auth = MpesaAccessToken()
                lipa_mpesa = LipanaMpesaPpassword()
                
                # Get credentials
                access_token = mpesa_auth.validated_mpesa_access_token
                password = lipa_mpesa.decode_password
                timestamp = lipa_mpesa.lipa_time
                business_shortcode = lipa_mpesa.Business_short_code

                # Prepare STK Push
                headers = {
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json"
                }

                payload = {
                    "BusinessShortCode": business_shortcode,
                    "Password": password,
                    "Timestamp": timestamp,
                    "TransactionType": "CustomerPayBillOnline",
                    "Amount": str(donation.amount),
                    "PartyA": donation.phone_number,
                    "PartyB": business_shortcode,
                    "PhoneNumber": donation.phone_number,
                    "CallBackURL": "https://yourdomain.com/mpesa-callback/",
                    "AccountReference": "CleanAirDonation",
                    "TransactionDesc": "Donation for Clean Air"
                }

                # Make request
                response = requests.post(
                    "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest",
                    headers=headers,
                    json=payload,
                    timeout=30
                )

                if response.status_code == 200:
                    response_data = response.json()
                    if response_data.get('ResponseCode') == "0":
                        donation.mpesa_request_id = response_data.get('MerchantRequestID')
                        donation.save()
                        messages.success(request, "Payment request sent to your phone!")
                        return redirect('advocates:donation_history')
                
                raise Exception(response.json().get('errorMessage', 'Payment failed'))

            except Exception as e:
                messages.error(request, f"Payment failed: {str(e)}")
                return redirect('advocates:initiate_donation')

    else:
        form = DonationForm()

    return render(request, 'advocates/donates.html', {'form': form})

@login_required
def donation_history(request):
    donations = Donation.objects.filter(user=request.user).order_by('-date')
    return render(request, 'donations/history.html', {'donations': donations})

def mpesa_callback(request):
    """Handle M-Pesa payment confirmation"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            callback_data = data.get('Body', {}).get('stkCallback', {})
            
            if callback_data.get('ResultCode') == 0:  # Success
                metadata = callback_data.get('CallbackMetadata', {}).get('Item', [])
                receipt_data = {item.get('Name'): item.get('Value') for item in metadata}
                
                donation = Donation.objects.filter(
                    mpesa_request_id=callback_data.get('MerchantRequestID')
                ).first()
                
                if donation:
                    donation.mpesa_receipt = receipt_data.get('MpesaReceiptNumber')
                    donation.is_confirmed = True
                    donation.save()
                    send_donation_receipt(donation)  # Send receipt email
            
            return HttpResponse(status=200)
        except Exception as e:
            print(f"Callback error: {str(e)}")
            return HttpResponse(status=400)
    return HttpResponse(status=405)

# ============ Warrior/Advocate Views ============
def warrior_list(request):
    warriors = CleanAirWarrior.objects.all()
    return render(request, 'advocates/list.html', {'warriors': warriors})

# ============ Consultation Views ============
def request_consultation(request):
    if request.method == 'POST':
        warrior_id = request.POST.get('warrior_id')
        name = request.POST.get('name')
        email = request.POST.get('email')
        issue = request.POST.get('issue')
        
        try:
            warrior = CleanAirWarrior.objects.get(id=warrior_id)
            
            # Save to database
            ConsultationRequest.objects.create(
                warrior=warrior,
                name=name,
                email=email,
                issue=issue
            )
            
            # Send email to admin
            send_mail(
                f"New Consultation Request for {warrior.name}",
                f"Name: {name}\nEmail: {email}\nIssue: {issue}",
                settings.DEFAULT_FROM_EMAIL,
                [settings.DEFAULT_FROM_EMAIL],
                fail_silently=False,
            )
            
            # Send confirmation to user
            send_mail(
                "Your Consultation Request Received",
                f"Dear {name},\n\nThank you for reaching out to {warrior.name}.\n\n"
                f"We've received your request regarding:\n{issue}\n\n"
                "The advocate will contact you within 48 hours.\n\n"
                "Best regards,\nClean Air Team",
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
            
            messages.success(request, "Your consultation request has been submitted!")
            return redirect('warrior_list')
            
        except Exception as e:
            messages.error(request, f"Error submitting request: {str(e)}")
            return redirect('warrior_list')
    
    return redirect('warrior_list')

# ============ Appointment Views ============
@login_required
def book_appointment(request, warrior_id):
    warrior = get_object_or_404(CleanAirWarrior, id=warrior_id)
    
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        date_str = request.POST.get('date')
        reason = request.POST.get('reason')
        
        try:
            appointment_date = timezone.datetime.strptime(date_str, '%Y-%m-%dT%H:%M')
            
            # Save appointment
            appointment = Appointment.objects.create(
                warrior=warrior,
                name=name,
                email=email,
                date=appointment_date,
                reason=reason
            )
            
            # Send confirmation email
            send_mail(
                f"Appointment Confirmation with {warrior.name}",
                f"Dear {name},\n\n"
                f"Your appointment with {warrior.name} has been scheduled for:\n"
                f"{appointment_date.strftime('%A, %B %d, %Y at %I:%M %p')}\n\n"
                f"Purpose: {reason}\n\n"
                "We'll send you a reminder before the appointment.\n\n"
                "Best regards,\nClean Air Team",
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
            
            messages.success(request, "Appointment booked successfully!")
            return redirect('warrior_list')
            
        except Exception as e:
            messages.error(request, f"Error booking appointment: {str(e)}")
    
    return render(request, 'appointments/book.html', {'warrior': warrior})

# ============ Receipt Views ============

@login_required
def download_receipt(request, donation_id):
    donation = get_object_or_404(Donation, id=donation_id)
    
    # Allow staff to download any receipt, or users to download their own
    if not request.user.is_staff and donation.user != request.user:
        messages.error(request, "You don't have permission to view this receipt")
        return redirect('advocates:donation_history')
    
    # if donation.status != 'confirmed':
    #     messages.warning(request, "This donation hasn't been confirmed yet")
    #     return redirect('advocates:donation_history')
    
    # Generate PDF using the imported function
    from .receipts import generate_receipt_pdf
    pdf_buffer = generate_receipt_pdf(donation)
    
    # Return PDF response
    response = HttpResponse(pdf_buffer.getvalue(), content_type='application/pdf')
    filename = f"donation_receipt_{donation.id}.pdf"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response
    
    messages.error(request, "Failed to generate receipt")
    return redirect('advocates:donation_history')

def donation_success(request):
    transaction_id = request.GET.get('transaction_id', 'N/A')
    return render(request, 'donations/success.html', {
        'transaction_id': transaction_id,
        'title': 'Donation Successful',
        'message': 'Thank you for your generous donation!',
        'details': 'Your contribution helps us improve air quality monitoring.'
    })

# ============ Helper Functions ============
def send_donation_receipt(donation):
    """Send donation receipt email with PDF attachment"""
    from django.core.mail import EmailMessage
    from django.conf import settings
    
    # Get the user's email from the user object
    recipient_email = donation.user.email if donation.user else None
    
    # If there's no email associated, we can't send the receipt
    if not recipient_email:
        print(f"No email found for donation #{donation.id}")
        return
    
    email = EmailMessage(
        "Your Donation Receipt",
        "Thank you for your support! Attached is your receipt.",
        settings.DEFAULT_FROM_EMAIL,
        [recipient_email],
    )
    
    receipt_pdf = donation.generate_receipt_pdf()
    email.attach(
        filename='receipt.pdf',
        content=receipt_pdf.getvalue(),
        mimetype='application/pdf'
    )
    email.send()
    

@staff_member_required
def confirm_payments(request):
    if request.method == 'POST':
        donation_id = request.POST.get('donation_id')
        receipt_number = request.POST.get('receipt_number')
        
        try:
            donation = Donation.objects.get(id=donation_id)
            donation.confirm_payment(request.user, receipt_number)
            messages.success(request, f"Donation #{donation_id} confirmed successfully!")
        except Donation.DoesNotExist:
            messages.error(request, "Donation not found")
        except Exception as e:
            messages.error(request, f"Error confirming payment: {str(e)}")
            
        return redirect('advocates:confirm_payments')
    
    # Get pending donations
    pending_donations = Donation.objects.filter(status='pending').order_by('-date')
    confirmed_donations = Donation.objects.filter(status='confirmed').order_by('-confirmation_date')[:10]
    
    return render(request, 'donations/confirm_payments.html', {
        'pending_donations': pending_donations,
        'confirmed_donations': confirmed_donations,
    })
    
@login_required
def view_receipt(request, donation_id):
    donation = get_object_or_404(Donation, id=donation_id)
    
    # Allow staff to view any receipt, or users to view their own
    if not request.user.is_staff and donation.user != request.user:
        messages.error(request, "You don't have permission to view this receipt")
        return redirect('advocates:donation_history')
    
    # if donation.status != 'confirmed':
    #     messages.warning(request, "This donation hasn't been confirmed yet")
    #     return redirect('advocates:donation_history')
    
    return render(request, 'advocates/receipt_view.html', {'donation': donation})    

# Add this to your views.py - this is just for testing purposes
@login_required
def update_donation_status(request, donation_id):
    donation = get_object_or_404(Donation, id=donation_id)
    
    # Only allow the user who made the donation or staff to update
    if not request.user.is_staff and donation.user != request.user:
        messages.error(request, "You don't have permission to update this donation")
        return redirect('advocates:donation_history')
    
    donation.status = 'confirmed'
    donation.mpesa_receipt = 'TEST-' + str(donation.id)  # Dummy receipt number
    donation.confirmation_date = timezone.now()
    donation.save()
    
    messages.success(request, "Donation status updated successfully!")
    return redirect('advocates:donation_history')

from django.shortcuts import get_object_or_404

def warrior_detail(request, pk):
    warrior = get_object_or_404(CleanAirWarrior, pk=pk)
    
    # Handle consultation form submission
    if request.method == 'POST' and 'consultation' in request.POST:
        form = ConsultationForm(request.POST)
        if form.is_valid():
            consultation = form.save(commit=False)
            consultation.warrior = warrior
            consultation.save()
            
            # Send emails
            send_consultation_emails(consultation)
            messages.success(request, "Your consultation request has been submitted!")
            return redirect('advocates:warrior_detail', pk=warrior.pk)
    
    # Handle appointment form submission        
    elif request.method == 'POST' and 'appointment' in request.POST:
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.warrior = warrior
            appointment.save()
            
            # Send confirmation email
            send_appointment_confirmation(appointment)
            messages.success(request, "Appointment booked successfully!")
            return redirect('advocates:warrior_detail', pk=warrior.pk)
    
    else:
        consultation_form = ConsultationForm()
        appointment_form = AppointmentForm()
    
    context = {
        'warrior': warrior,
        'consultation_form': consultation_form,
        'appointment_form': appointment_form,
    }
    return render(request, 'advocates/warrior_detail.html', context)

def send_consultation_emails(consultation):
    # Email to admin
    send_mail(
        f"New Consultation Request for {consultation.warrior.name}",
        f"Details:\nName: {consultation.name}\nEmail: {consultation.email}\nIssue: {consultation.issue}",
        settings.DEFAULT_FROM_EMAIL,
        [settings.ADMIN_EMAIL],
        fail_silently=False,
    )
    
    # Email to user
    send_mail(
        "Consultation Request Received",
        f"Dear {consultation.name},\n\nWe've received your request regarding:\n{consultation.issue}\n\n{consultation.warrior.name} will respond within 48 hours.",
        settings.DEFAULT_FROM_EMAIL,
        [consultation.email],
        fail_silently=False,
    )

def send_appointment_confirmation(appointment):
    send_mail(
        f"Appointment Confirmation with {appointment.warrior.name}",
        f"Dear {appointment.name},\n\n"
        f"Your appointment is scheduled for:\n"
        f"{appointment.date.strftime('%A, %B %d, %Y at %I:%M %p')}\n\n"
        f"Purpose: {appointment.reason}\n\n"
        "We'll send a reminder 24 hours before your appointment.",
        settings.DEFAULT_FROM_EMAIL,
        [appointment.email],
        fail_silently=False,
    )
    

def default_warrior_detail(request):
    # Get the first warrior or any specific one you want as default
    warrior = CleanAirWarrior.objects.first()
    if not warrior:
        raise Http404("No warriors available")
    return redirect('advocates:warrior_detail', pk=warrior.pk)    