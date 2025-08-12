import stripe, json
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt

stripe.api_key = settings.STRIPE_SECRET_KEY
ENDPOINT_SECRET = settings.STRIPE_WEBHOOK_SECRET

@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE", "")
    try:
        event = stripe.Webhook.construct_event(payload, sig_header, ENDPOINT_SECRET)
    except ValueError:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        return HttpResponse(status=400)

    # Manejo de eventos relevantes
    typ = event["type"]
    data = event["data"]["object"]

    if typ == "payment_intent.succeeded":
        pi = data
        # buscar la order por metadata/stripe_payment_intent_id y marcar como paid
    elif typ == "payment_intent.payment_failed":
        # notificar/actualizar orden
        pass
    # otros eventos: charge.refunded, charge.dispute.created, customer.subscription.updated, etc.

    return HttpResponse(status=200)
