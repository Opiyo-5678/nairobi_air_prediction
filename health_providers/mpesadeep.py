import requests
import base64
import datetime
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class MpesaAPI:
    def __init__(self):
        self.consumer_key = settings.MPESA_CONFIG['MPESA_CONSUMER_KEY']
        self.consumer_secret = settings.MPESA_CONFIG['MPESA_CONSUMER_SECRET']
        self.business_shortcode = settings.MPESA_CONFIG['MPESA_SHORTCODE']
        self.passkey = settings.MPESA_CONFIG['MPESA_PASSKEY']
        self.callback_url = settings.MPESA_CONFIG['MPESA_CALLBACK_URL']
        self.environment = settings.MPESA_CONFIG['ENVIRONMENT']
        self.transaction_type = settings.MPESA_CONFIG['TRANSACTION_TYPE']
        
        self.base_url = (
            "https://sandbox.safaricom.co.ke" 
            if self.environment == "sandbox" 
            else "https://api.safaricom.co.ke"
        )
        self.token_expiry = None
        self.access_token = None


    def get_access_token(self):
        """Get M-Pesa API access token with caching"""
        if self.access_token and self.token_expiry and self.token_expiry > datetime.datetime.now():
            return self.access_token
            
        url = f"{self.base_url}/oauth/v1/generate?grant_type=client_credentials"
        auth = base64.b64encode(f"{self.consumer_key}:{self.consumer_secret}".encode()).decode()
        
        try:
            response = requests.get(url, headers={"Authorization": f"Basic {auth}"}, timeout=30)
            response.raise_for_status()
            data = response.json()
            self.access_token = data.get("access_token")
            # Set token expiry 5 minutes before actual expiry
            expires_in = int(data.get("expires_in", 3599)) - 300
            self.token_expiry = datetime.datetime.now() + datetime.timedelta(seconds=expires_in)
            return self.access_token
        except requests.exceptions.RequestException as e:
            logger.error(f"Token request failed: {str(e)}")
            raise Exception(f"Failed to get token: {str(e)}")

    def generate_password(self):
        """Generate LIPA Na M-Pesa password with proper timestamp"""
        timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        password_str = f"{self.business_shortcode}{self.passkey}{timestamp}"
        return base64.b64encode(password_str.encode()).decode(), timestamp

    def initiate_stk_push(self, phone_number, amount, account_reference):
        """Improved STK Push with better sandbox handling"""
        try:
            # Format phone number first
            phone_number = self.format_phone_number(phone_number)
            
            # Sandbox-specific adjustments (only if in sandbox mode)
            if self.environment == "sandbox":
                test_conditions = {
                    "phone": "254708374149",  # Sandbox test number
                    "amount": "1",           # Fixed test amount
                    "account_ref": "TEST" + account_reference[-6:]  # Modified reference
                }
                print(f"\nSANDBOX MODE: Using test parameters - {test_conditions}\n")
            else:
                test_conditions = None
                
            # Generate authentication
            access_token = self.get_access_token()
            password, timestamp = self.generate_password()

            # Prepare request - use consistent business shortcode
            url = f"{self.base_url}/mpesa/stkpush/v1/processrequest"
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }

            payload = {
                "BusinessShortCode": self.business_shortcode,  # Use initialized value
                "Password": password,
                "Timestamp": timestamp,
                "TransactionType": "CustomerPayBillOnline",
                "Amount": str(test_conditions["amount"]) if test_conditions else str(amount),
                "PartyA": test_conditions["phone"] if test_conditions else phone_number,
                "PartyB": self.business_shortcode,
                "PhoneNumber": test_conditions["phone"] if test_conditions else phone_number,
                "CallBackURL": self.callback_url,
                "AccountReference": test_conditions["account_ref"] if test_conditions else account_reference[:12],
                "TransactionDesc": "Payment"[:13]  # Max 13 chars
            }

            # Debug output
            print("\n=== MPesa Request ===")
            print("Environment:", self.environment)
            print("URL:", url)
            print("Headers:", {k: "*****" if k == "Authorization" else v for k, v in headers.items()})
            print("Payload:", payload)
            
            # Make request
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            response_data = response.json()
            
            print("Response:", response_data)
            print("=== End Debug ===")

            # Handle response
            if response.status_code == 200 and 'ResponseCode' in response_data:
                if response_data['ResponseCode'] == "0":
                    return {
                        "success": True,
                        "checkout_request_id": response_data["CheckoutRequestID"],
                        "merchant_request_id": response_data["MerchantRequestID"],
                        "response_description": response_data["ResponseDescription"],
                        "is_sandbox": self.environment == "sandbox"
                    }
                return {
                    "success": False,
                    "error": response_data.get('errorMessage', 
                            response_data.get('ResponseDescription', 'Request failed')),
                    "response": response_data
                }
            return {
                "success": False,
                "error": f"HTTP {response.status_code}",
                "response": response_data
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
            
    def verify_payment(self, checkout_request_id):
        """Check payment status with proper error handling"""
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

            logger.info(f"Querying payment status for: {checkout_request_id}")
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            response_data = response.json()

            if response.status_code == 200:
                result_code = response_data.get("ResultCode")
                if result_code == "0":
                    # Extract payment details from callback metadata
                    items = response_data.get("CallbackMetadata", {}).get("Item", [])
                    receipt = next((item["Value"] for item in items if item.get("Name") == "MpesaReceiptNumber"), None)
                    amount = next((item["Value"] for item in items if item.get("Name") == "Amount"), None)
                    phone = next((item["Value"] for item in items if item.get("Name") == "PhoneNumber"), None)
                    
                    return {
                        "success": True,
                        "status": "completed",
                        "mpesa_receipt": receipt,
                        "phone_number": phone,
                        "amount": amount,
                        "result_desc": response_data.get("ResultDesc")
                    }
                else:
                    return {
                        "success": True,
                        "status": "failed",
                        "result_code": result_code,
                        "result_desc": response_data.get("ResultDesc")
                    }
            
            logger.error(f"Payment query failed: {response.status_code} - {response.text}")
            return {
                "success": False,
                "error": f"API request failed with status {response.status_code}",
                "response_data": response_data
            }

        except Exception as e:
            logger.error(f"Exception in payment query: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }
            
@staticmethod
def format_phone_number(phone):
        """Convert phone number to MPesa format (254...) with better validation"""
        if not phone:
            raise ValueError("Phone number cannot be empty")
            
        phone = str(phone).strip()
        
        # Remove any non-digit characters
        phone = ''.join(c for c in phone if c.isdigit())
        
        # Handle common Kenyan formats
        if phone.startswith('0') and len(phone) == 10:  # 07... or 011...
            return '254' + phone[1:]
        elif phone.startswith('254') and len(phone) == 12:
            return phone
        elif phone.startswith('7') and len(phone) == 9:  # 7...
            return '254' + phone
        elif len(phone) == 12 and not phone.startswith('254'):  # If someone sends 254... with wrong prefix
            return '254' + phone[-9:]
        elif len(phone) == 9:  # Bare number without prefix
            return '254' + phone
        else:
            raise ValueError(f"Invalid phone number format: {phone}. Expected 07..., 011..., 254..., or 7...")
        
def verify_multiple_payments(self, checkout_ids):
        """Verify multiple payments in a single request"""
        results = {}
        for checkout_id in checkout_ids:
            results[checkout_id] = self.verify_payment(checkout_id)
        return results
    
def reverse_transaction(self, transaction_id, amount, receiver_party):
    """Initiate transaction reversal"""
    try:
        access_token = self.get_access_token()
        url = f"{self.base_url}/mpesa/reversal/v1/request"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "Initiator": self.business_shortcode,
            "SecurityCredential": self._generate_security_credential(),
            "CommandID": "TransactionReversal",
            "TransactionID": transaction_id,
            "Amount": str(amount),
            "ReceiverParty": receiver_party,
            "RecieverIdentifierType": "4",  # Organization
            "ResultURL": f"{self.callback_url}/reversal",
            "QueueTimeOutURL": f"{self.callback_url}/reversal/timeout",
            "Remarks": "Refund",
            "Occasion": "Customer request"
        }
        
        response = requests.post(url, json=payload, headers=headers)
        return response.json()
    except Exception as e:
        logger.error(f"Reversal failed: {str(e)}")
        return {"success": False, "error": str(e)}    