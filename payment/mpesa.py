import requests
from django.conf import settings
from requests.auth import HTTPBasicAuth
import base64
import datetime
import json
from .models import STKPushTransaction, B2CPayment


# from daraja_client.core import DarajaClient
# from decouple import config

# # Configuration
# auth_url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
# stk_push_url = 'https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest'
# call_back_url = 'http://127.0.0.1:8000/payment/stk-callback/' # 
# phone_number = '+254740562740' # person to receive the prompt
# amount = 1


# # Initialize the client
# cl = DarajaClient(
#     auth_url=auth_url,
#     consumer_key=settings.MPESA_CONFIG["CONSUMER_KEY"],
#     consumer_secret=settings.MPESA_CONFIG["CONSUMER_SECRET"],
#     pass_key=settings.MPESA_CONFIG["PASSKEY"],
#     shortcode=settings.MPESA_CONFIG["SHORTCODE"],
#     phone_number=phone_number,
#     call_back_url=call_back_url,
#     amount=amount
# )

# # Send STK Push
# response = cl.send_stk_push(stk_push_url=stk_push_url)
# print(response)

def get_access_token():
    """Fetch access token from Safaricom API."""
    url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    if settings.MPESA_CONFIG["ENV"] == "production":
        url = "https://api.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"

    response = requests.get(
        url,
        auth=HTTPBasicAuth(
            settings.MPESA_CONFIG["CONSUMER_KEY"],
            settings.MPESA_CONFIG["CONSUMER_SECRET"]
        ),
    )
    
    return response.json().get("access_token")

def stk_push_request(phone_number, amount, account_reference="Test Payment", transaction_desc="Payment"):
    """Send STK Push request to M-Pesa and save transaction."""
    access_token = get_access_token()
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    
    password = base64.b64encode(
        (settings.MPESA_CONFIG["SHORTCODE"] + settings.MPESA_CONFIG["PASSKEY"] + timestamp).encode()
    ).decode("utf-8")

    payload = {
        "BusinessShortCode": 174379, #settings.MPESA_CONFIG["SHORTCODE"],
        "Password": 'MTc0Mzc5YmZiMjc5ZjlhYTliZGJjZjE1OGU5N2RkNzFhNDY3Y2QyZTBjODkzMDU5YjEwZjc4ZTZiNzJhZGExZWQyYzkxOTIwMjUwMjE3MjEzNzQ5', # password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": 2, # amount,
        "PartyA": 254740562740, # phone_number,
        "PartyB": 174379, #settings.MPESA_CONFIG["SHORTCODE"],
        "PhoneNumber":254740562740, # phone_number,
        "CallBackURL": settings.MPESA_CONFIG["CALLBACK_URL"],
        "AccountReference": account_reference,
        "TransactionDesc": transaction_desc,
    }

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    response = requests.post(
        "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest",
        headers=headers,
        json=payload,
    )

    response_data = response.json()

    # Save transaction to database
    STKPushTransaction.objects.create(
        phone_number=phone_number,
        amount=amount,
        merchant_request_id=response_data.get("MerchantRequestID", ""),
        checkout_request_id=response_data.get("requestId", ""),
    )

    return response_data

def b2c_payment(phone_number, amount):
    """Send B2C payment and save transaction."""
    access_token = get_access_token()
    
    payload = {
        "InitiatorName": settings.MPESA_CONFIG["INITIATOR_NAME"],
        "SecurityCredential": settings.MPESA_CONFIG["INITIATOR_PASSWORD"],
        "CommandID": "BusinessPayment",
        "Amount": amount,
        "PartyA": settings.MPESA_CONFIG["SHORTCODE"],
        "PartyB": phone_number,
        "Remarks": "Salary Payment",
        "QueueTimeOutURL": settings.MPESA_CONFIG["CALLBACK_URL"] + "b2c-callback/",
        "ResultURL": settings.MPESA_CONFIG["CALLBACK_URL"] + "b2c-callback/",
        "Occasion": "Payment",
    }

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    response = requests.post(
        "https://sandbox.safaricom.co.ke/mpesa/b2c/v1/paymentrequest",
        headers=headers,
        json=payload,
    )

    response_data = response.json()

    # Save transaction to database
    B2CPayment.objects.create(
        phone_number=phone_number,
        amount=amount,
        transaction_id=response_data.get("TransactionID", None),
    )

    return response_data
