from django.urls import include, path
from .views import (
    EmployeeListAPIView,
    EmployeeRetrieveAPIView,
    EmployeeTransactionsListCreateAPIView,
    EmployeeArchiveAPIView,
)


transaction_urls = [
    path("transactions/", include("data.employee.transactions.urls")),
    path(
        "<uuid:employee>/transactions", EmployeeTransactionsListCreateAPIView.as_view()
    ),
]

urlpatterns = [
    path("", EmployeeListAPIView.as_view()),
    path("<uuid:pk>", EmployeeRetrieveAPIView.as_view()),
    path("<uuid:pk>/archive", EmployeeArchiveAPIView.as_view()),
    # Urls for transactions
    *transaction_urls,
]
