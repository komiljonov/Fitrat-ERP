from django.urls import path
from .views import (
    EmployeeTransactionsListCreateAPIView,
    EmployeeTransactionRetrieveDestroyAPIView,
)


urlpatterns = [
    path("", EmployeeTransactionsListCreateAPIView.as_view()),
    path("<uuid:pk>", EmployeeTransactionRetrieveDestroyAPIView.as_view()),
]
