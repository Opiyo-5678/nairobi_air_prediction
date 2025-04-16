import requests
import datetime
import base64
from django.conf import settings
from ecommerce.models import Payment  # Import the Payment model


def get_mpesa_access_token():
    """Fetches M-Pesa access token from Safaricom API"""
    api_url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    credentials = f"{settings.MPESA_CONSUMER_KEY}:{settings.MPESA_CONSUMER_SECRET}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()

    headers = {
        "Authorization": f"Basic {encoded_credentials}"
    }

    response = requests.get(api_url, headers=headers)
    token_data = response.json()

    return token_data.get("access_token")  # Returns the access token


def generate_password():
    """Generates password for M-Pesa STK Push"""
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    data_to_encode = settings.MPESA_SHORTCODE + settings.MPESA_PASSKEY + timestamp
    encoded_string = base64.b64encode(data_to_encode.encode()).decode()
    return encoded_string, timestamp


def lipa_na_mpesa(phone, amount):
    """Initiates M-Pesa STK Push payment request"""
    password, timestamp = generate_password()
    access_token = get_mpesa_access_token()  # Fetch access token dynamically

    payload = {
        "BusinessShortCode": settings.MPESA_SHORTCODE,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": phone,
        "PartyB": settings.MPESA_SHORTCODE,
        "PhoneNumber": phone,
        "CallBackURL": settings.MPESA_CALLBACK_URL,
        "AccountReference": "EcommerceApp",
        "TransactionDesc": "Payment for Order"
    }

    headers = {
        "Authorization": f"Bearer {access_token}",  # Use dynamically fetched token
        "Content-Type": "application/json"
    }

    response = requests.post(
        "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest",
        json=payload,
        headers=headers
    )

    response_data = response.json()

    # Save transaction to the database
    Payment = Payment.objects.create(
        phone_number=phone,
        amount=amount,
        transaction_id=response_data.get("CheckoutRequestID", None),
        status="Pending"
    )

    return response_data
