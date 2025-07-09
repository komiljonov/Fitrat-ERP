from django.urls import include, path
from .views import PaycomWebhookView


urlpatterns = [
    path('transaction/', PaycomWebhookView.as_view(), name='paycom-webhook'),
]