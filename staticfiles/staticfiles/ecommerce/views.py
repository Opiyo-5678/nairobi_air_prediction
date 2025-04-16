from rest_framework import generics
from django.http import JsonResponse
from .models import Product, Order, Payment
from .serializers import ProductSerializer, OrderSerializer
from .mpesa import lipa_na_mpesa
import json
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from rest_framework.parsers import MultiPartParser, FormParser


def initiate_payment(request):
    phone_number = request.GET.get("phone")
    amount = request.GET.get("amount")

    if not phone_number or not amount:
        return JsonResponse({"error": "Phone number and amount are required"}, status=400)

    response = lipa_na_mpesa(phone_number, int(amount))
    return JsonResponse(response)


class ProductListView(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    parser_classes = (MultiPartParser, FormParser)


class OrderCreateView(generics.CreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer


@method_decorator(csrf_exempt, name='dispatch')
class MpesaCallbackView(View):
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)

        try:
            checkout_request_id = data["Body"]["stkCallback"]["CheckoutRequestID"]
            result_code = data["Body"]["stkCallback"]["ResultCode"]
            mpesa_receipt_number = None

            if result_code == 0:  # Successful transaction
                mpesa_receipt_number = data["Body"]["stkCallback"]["CallbackMetadata"]["Item"][1]["Value"]

                # Update payment in database
                payment = Payment.objects.get(transaction_id=checkout_request_id)
                payment.mpesa_receipt_number = mpesa_receipt_number
                payment.status = "Completed"
                payment.save()
                
                order = Order.objects.get(payment=payment)
                order.status = "Paid"
                order.save()

            else:  # Failed transaction
                payment = Payment.objects.get(transaction_id=checkout_request_id)
                payment.status = "Failed"
                payment.save()

        except Payment.DoesNotExist:
            return JsonResponse({"error": "Payment not found"}, status=404)

        return JsonResponse({"message": "Payment status updated"})
