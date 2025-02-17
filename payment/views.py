from django.shortcuts import render

# Create your views here.
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import STKPushTransaction, B2CPayment
from .mpesa import stk_push_request, b2c_payment

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .mpesa import stk_push_request, b2c_payment

@csrf_exempt
def stk_push(request):
    """Handle STK Push request."""
    phone_number =254740562740 # request.GET.get("phone_number")
    amount = 1 # request.GET.get("amount")
    
    if not phone_number or not amount:
        return JsonResponse({"error": "Phone number and amount are required"}, status=400)
    
    response = stk_push_request(phone_number, int(amount))
    return JsonResponse(response)

@csrf_exempt
def b2c_pay(request):
    """Handle B2C Payment request."""
    phone_number = request.GET.get("phone_number")
    amount = request.GET.get("amount")
    
    if not phone_number or not amount:
        return JsonResponse({"error": "Phone number and amount are required"}, status=400)

    response = b2c_payment(phone_number, int(amount))
    return JsonResponse(response)


@csrf_exempt
def stk_push_callback(request):
    """Handle M-Pesa STK Push callback."""
    try:
        data = json.loads(request.body.decode("utf-8"))
        body = data.get("Body", {}).get("stkCallback", {})

        merchant_request_id = body.get("MerchantRequestID")
        checkout_request_id = body.get("CheckoutRequestID")
        result_code = body.get("ResultCode")
        result_desc = body.get("ResultDesc")

        transaction = STKPushTransaction.objects.filter(
            checkout_request_id=checkout_request_id
        ).first()

        if transaction:
            transaction.result_code = result_code
            transaction.result_desc = result_desc
            transaction.status = "Failed" if result_code != 0 else "Successful"

            # Extract transaction ID if successful
            if result_code == 0:
                transaction_details = body.get("CallbackMetadata", {}).get("Item", [])
                for item in transaction_details:
                    if item.get("Name") == "MpesaReceiptNumber":
                        transaction.transaction_id = item.get("Value")
                        break

            transaction.save()

        return JsonResponse({"message": "Callback received"}, status=200)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


@csrf_exempt
def b2c_callback(request):
    """Handle M-Pesa B2C callback."""
    try:
        data = json.loads(request.body.decode("utf-8"))
        body = data.get("Result", {})

        transaction_id = body.get("TransactionID")
        result_code = body.get("ResultCode")
        result_desc = body.get("ResultDesc")

        transaction = B2CPayment.objects.filter(transaction_id=transaction_id).first()

        if transaction:
            transaction.result_code = result_code
            transaction.result_desc = result_desc
            transaction.status = "Failed" if result_code != 0 else "Successful"
            transaction.save()

        return JsonResponse({"message": "B2C callback received"}, status=200)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)
