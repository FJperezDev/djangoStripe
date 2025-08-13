import stripe
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

stripe.api_key = settings.STRIPE_SECRET_KEY

class CreatePaymentIntentView(APIView):
    permission_classes = [permissions.IsAuthenticated]  # ajusta según tu auth

    def post(self, request):
        # recalcula el monto en servidor usando tu carrito/orden. NO confiar en el cliente.
        # ejemplo mínimo: recibir order_id y buscarlo en BD (aquí simplificado)
        try:
            amount = int(request.data.get("amount"))  # en céntimos
            currency = request.data.get("currency", "eur")
            # opcional: attach to customer if exists
            intent = stripe.PaymentIntent.create(
                amount=amount,
                currency=currency,
                metadata={"user_id": request.user.id},
                # setup_future_usage="off_session" si quieres guardar método
            )
            return Response({"clientSecret": intent.client_secret})
        except stripe.error.StripeError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class GetPublishableKey(APIView):

    def get(self, request):
        return Response({'publishableKey':settings.STRIPE_PUBLISHABLE_KEY})


class PaymentSheetCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:

            amount = int(request.data.get("amount", 0))
            if amount <= 0:
                return Response({"error": "Amount inválido"}, status=400)

            customer = stripe.Customer.create(email=request.user.email)
            payment_intent = stripe.PaymentIntent.create(
                amount=amount,
                currency="eur",
                customer=customer.id,
            )
            ephemeral_key = stripe.EphemeralKey.create(
                customer=customer.id,
                stripe_version="2022-11-15"
            )
            return Response({
                "paymentIntent": payment_intent.client_secret,
                "ephemeralKey": ephemeral_key.secret,
                "customer": customer.id,
                "publishableKey": settings.STRIPE_PUBLISHABLE_KEY,
            })
        except Exception as e:
            import traceback
            print("Error en PaymentSheetCreateView:", e)
            traceback.print_exc()
            return Response({"error": str(e)}, status=500)
