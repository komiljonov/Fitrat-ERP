# payments/urls.py

from django.urls import path
from .views import GeneratePaymeURLView, PaycomWebhookView, TransactionAPIView

urlpatterns = [
    path("paycom", GeneratePaymeURLView.as_view(), name="paycom-webhook"),
    path("payme", PaycomWebhookView.as_view(), name="generate-payment-link"),
    path("transaction/", TransactionAPIView.as_view(), name="transaction-api"),
]
