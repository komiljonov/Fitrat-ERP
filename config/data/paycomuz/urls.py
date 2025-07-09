# payments/urls.py

from django.urls import path
from .views import GeneratePaymeURLView, PaycomWebhookView

urlpatterns = [
    path("paycom/", PaycomWebhookView.as_view(), name="paycom-webhook"),
    path("generate-payment/", GeneratePaymeURLView.as_view(), name="generate-payment-link"),
]
