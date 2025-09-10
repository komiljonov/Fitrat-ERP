from django.urls import path
from .views import EmployeeListAPIView, EmployeeTransactionsListCreateAPIView

urlpatterns = [
    path("", EmployeeListAPIView.as_view()),
    path(
        "<uuid:employee>/transactions", EmployeeTransactionsListCreateAPIView.as_view()
    ),
]
