from django.urls import include, path
from .views import (
    EmployeeListAPIView,
    EmployeeRetrieveAPIView,
    EmployeeTransactionsListCreateAPIView,
    EmployeeArchiveAPIView,
    EmployeeRelatedObjectsAPIView,
)


transaction_urls = [
    path("transactions/", include("data.employee.transactions.urls")),
    path(
        "<uid:employee>/transactions", EmployeeTransactionsListCreateAPIView.as_view()
    ),
]

urlpatterns = [
    path("", EmployeeListAPIView.as_view()),
    path("<uuid:pk>", EmployeeRetrieveAPIView.as_view()),
    path("<uuid:pk>/archive", EmployeeArchiveAPIView.as_view()),
    path("<uuid:pk>/related_objects", EmployeeRelatedObjectsAPIView.as_view()),
    # Urls for transactions
    *transaction_urls,
]
