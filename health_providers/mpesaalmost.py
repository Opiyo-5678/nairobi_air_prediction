import requests
import base64
import datetime
import uuid
from django.conf import settings

class MpesaAPI:
    def __init__(self, consumer_key, consumer_secret, business_shortcode, 
        passkey, callback_url, environment="sandbox"):
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.business_shortcode = business_shortcode
        self.passkey = passkey
        self.callback_url = callback_url
        
        if environment == "sandbox":
            self.base_url = "https://sandbox.safaricom.co.ke"
        else:
            self.base_url = "https://api.safaricom.co.ke"

    def get_access_token(self):
        """Get M-Pesa API access token"""
        url = f"{self.base_url}/oauth/v1/generate?grant_type=client_credentials"
        auth = base64.b64encode(f"{self.consumer_key}:{self.consumer_secret}".encode()).decode()
        
        headers = {"Authorization": f"Basic {auth}"}
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            return response.json().get("access_token")
        raise Exception(f"Failed to get token: {response.text}")

    def generate_password(self):
        """Generate LIPA Na M-Pesa password"""
        timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        password_str = f"{self.business_shortcode}{self.passkey}{timestamp}"
        return base64.b64encode(password_str.encode()).decode(), timestamp

    def initiate_stk_push(self, phone_number, amount, account_reference):
        """Initiate STK Push with enhanced validation"""
        try:
            # Format phone number (ensure 254 format)
            phone_number = self.format_phone_number(phone_number)
            
            access_token = self.get_access_token()
            password, timestamp = self.generate_password()

            url = f"{self.base_url}/mpesa/stkpush/v1/processrequest"
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }

            payload = {
                "BusinessShortCode": self.business_shortcode,
                "Password": password,
                "Timestamp": timestamp,
                "TransactionType": "CustomerPayBillOnline",
                "Amount": amount,
                "PartyA": phone_number,
                "PartyB": self.business_shortcode,
                "PhoneNumber": phone_number,
                "CallBackURL": self.callback_url,
                "AccountReference": account_reference,
                "TransactionDesc": "Payment for services"
            }

            response = requests.post(url, json=payload, headers=headers)
            response_data = response.json()

            if response.status_code == 200:
                return {
                    "success": True,
                    "checkout_request_id": response_data.get("CheckoutRequestID"),
                    "merchant_request_id": response_data.get("MerchantRequestID"),
                    "response_description": response_data.get("ResponseDescription")
                }
            return {
                "success": False,
                "error": response_data.get("errorMessage", "Unknown error")
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def verify_payment(self, checkout_request_id):
        """Check if payment was completed"""
        try:
            access_token = self.get_access_token()
            password, timestamp = self.generate_password()

            url = f"{self.base_url}/mpesa/stkpushquery/v1/query"
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }

            payload = {
                "BusinessShortCode": self.business_shortcode,
                "Password": password,
                "Timestamp": timestamp,
                "CheckoutRequestID": checkout_request_id
            }

            response = requests.post(url, json=payload, headers=headers)
            response_data = response.json()

            if response.status_code == 200:
                result_code = response_data.get("ResultCode")
                if result_code == "0":
                    return {
                        "success": True,
                        "status": "completed",
                        "mpesa_receipt": response_data.get("CallbackMetadata", {}).get("Item", [{}])[1].get("Value"),
                        "phone_number": response_data.get("PhoneNumber"),
                        "amount": response_data.get("Amount")
                    }
                return {
                    "success": True,
                    "status": "failed",
                    "result_desc": response_data.get("ResultDesc")
                }
            return {
                "success": False,
                "error": response_data.get("errorMessage", "Query failed")
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    @staticmethod
    def format_phone_number(phone):
        """Convert phone number to MPesa format (254...)"""
        if phone.startswith("+"):
            phone = phone[1:]
        if phone.startswith("254"):
            return phone
        if phone.startswith("0"):
            return "254" + phone[1:]
        return phone  # Fallback (may fail)