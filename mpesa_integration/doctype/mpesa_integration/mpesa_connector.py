import requests
import datetime
import base64
from requests.auth import HTTPBasicAuth

class MpesaConnector:
    def __init__(self, env="sandbox", consumer_key=None, consumer_secret=None, business_shortcode=None, online_passkey=None, till_number=None):
        self.env = env
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.business_shortcode = business_shortcode
        self.online_passkey = online_passkey
        self.till_number = till_number
        self.base_url = "https://sandbox.safaricom.co.ke" if env == "sandbox" else "https://api.safaricom.co.ke"
        self.authenticate()

    def authenticate(self):
        auth_url = f"{self.base_url}/oauth/v1/generate?grant_type=client_credentials"
        response = requests.get(auth_url, auth=HTTPBasicAuth(self.consumer_key, self.consumer_secret))
        self.access_token = response.json()["access_token"]

    def stk_push(self, phone_number, amount, account_reference, transaction_desc):
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        password = base64.b64encode(f"{self.business_shortcode}{self.online_passkey}{timestamp}".encode()).decode("utf-8")
        payload = {
            "BusinessShortCode": self.business_shortcode,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": amount,
            "PartyA": phone_number,
            "PartyB": self.business_shortcode,
            "PhoneNumber": phone_number,
            "CallBackURL": "/api/method/mpesa_integration.mpesa_settings.mpesa_settings.verify_transaction",
            "AccountReference": account_reference,
            "TransactionDesc": transaction_desc
        }
        headers = {"Authorization": f"Bearer {self.access_token}", "Content-Type": "application/json"}
        url = f"{self.base_url}/mpesa/stkpush/v1/processrequest"
        response = requests.post(url, json=payload, headers=headers)
        return response.json()
