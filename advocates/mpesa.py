import requests
import json
from requests.auth import HTTPBasicAuth
from datetime import datetime
import base64

class MpesaC2bCredential:
    consumer_key = '1ktP51i1jECFDDd8UdimELCE2cAZyjO4Uz6ufF5GDbpohIpd'
    consumer_secret = 'qUbtwAnveOESfoJ7M8sj0CbeQww6TmvpzMcoWiQm5iGwlKPGrF65MlZ65dmuZ5f1'
    api_URL = 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'

class MpesaAccessToken:
    @classmethod
    def get_token(cls):
        try:
            response = requests.get(
                MpesaC2bCredential.api_URL,
                auth=HTTPBasicAuth(MpesaC2bCredential.consumer_key, MpesaC2bCredential.consumer_secret),
                headers={'Cache-Control': 'no-cache'},
                timeout=30
            )
            response.raise_for_status()
            return response.json()["access_token"]
        except Exception as e:
            raise Exception(f"Failed to get M-Pesa token: {str(e)}")

    @property
    def validated_mpesa_access_token(self):
        return self.get_token()

class LipanaMpesaPpassword:
    def __init__(self):
        self.lipa_time = datetime.now().strftime('%Y%m%d%H%M%S')
        self.Business_short_code = "174379"
        self.passkey = 'bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919'
    
    @property
    def decode_password(self):
        data_to_encode = f"{self.Business_short_code}{self.passkey}{self.lipa_time}"
        return base64.b64encode(data_to_encode.encode()).decode('utf-8')