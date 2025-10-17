from django.urls import path

from data.student.transactions.views import TransactionListAPIView

urlpatterns = [
    path("", TransactionListAPIView.as_view(), name="transactions"),
]
