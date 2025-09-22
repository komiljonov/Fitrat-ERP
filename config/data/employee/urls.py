from django.urls import include, path
from .views import (
    EmployeeListAPIView,
    EmployeeRetrieveAPIView,
    EmployeeTransactionsListCreateAPIView,
)

urlpatterns = [
    path("", EmployeeListAPIView.as_view()),
    path("<uuid:pk>", EmployeeRetrieveAPIView.as_view()),
    path("transactions/", include("data.employee.transactions.urls")),
    path(
        "<uuid:employee>/transactions", EmployeeTransactionsListCreateAPIView.as_view()
    ),
]
