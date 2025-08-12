from django.db import models
from django.contrib.auth import get_user_model

from .user import CustomUser

CustomUser = get_user_model()

class Order(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True)
    amount = models.IntegerField()   # en céntimos
    currency = models.CharField(max_length=8, default="eur")
    stripe_payment_intent_id = models.CharField(max_length=255, blank=True, null=True)
    paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)