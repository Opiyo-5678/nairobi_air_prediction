import requests
import base64
import datetime
import uuid

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
        auth = base64.b64encode(f"{self.consumer_key}:{self.consumer_secret}".encode()).decode("utf-8")
        
        headers = {
            "Authorization": f"Basic {auth}"
        }
        
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            result = response.json()
            return result.get("access_token")
        else:
            raise Exception(f"Failed to get access token: {response.text}")
    
    def generate_password(self):
        """Generate password for STK Push"""
        timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        password_str = f"{self.business_shortcode}{self.passkey}{timestamp}"
        password_bytes = password_str.encode('utf-8')
        return base64.b64encode(password_bytes).decode('utf-8'), timestamp
    
    def initiate_stk_push(self, phone_number, amount, account_reference, transaction_desc):
        """Initiate STK Push transaction"""
        try:
            access_token = self.get_access_token()
            
            if not access_token:
                return {"success": False, "message": "Failed to get access token"}
            
            password, timestamp = self.generate_password()
            
            # Format phone number
            if phone_number.startswith("+"):
                phone_number = phone_number[1:]
            if phone_number.startswith("254"):
                phone_number = "254" + phone_number[3:]
            elif phone_number.startswith("0"):
                phone_number = "254" + phone_number[1:]
            
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
                "Amount": int(amount),
                "PartyA": phone_number,
                "PartyB": self.business_shortcode,
                "PhoneNumber": phone_number,
                "CallBackURL": self.callback_url,
                "AccountReference": account_reference,
                "TransactionDesc": transaction_desc
            }
            
            response = requests.post(url, json=payload, headers=headers)
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "success": True,
                    "checkout_request_id": result.get("CheckoutRequestID"),
                    "response": result
                }
            else:
                return {
                    "success": False,
                    "message": f"Failed to initiate payment: {response.text}"
                }
        except Exception as e:
            return {
                "success": False,
                "message": f"An error occurred: {str(e)}"
            }
    
    def check_payment_status(self, checkout_request_id):
        """Check the status of a payment"""
        try:
            access_token = self.get_access_token()
            
            if not access_token:
                return {"success": False, "message": "Failed to get access token"}
            
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
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "success": True,
                    "result": result
                }
            else:
                return {
                    "success": False,
                    "message": f"Failed to check payment status: {response.text}"
                }
        except Exception as e:
            return {
                "success": False,
                "message": f"An error occurred: {str(e)}"
            }