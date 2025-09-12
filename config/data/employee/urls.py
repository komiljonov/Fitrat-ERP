from django.urls import include, path
from .views import EmployeeListAPIView, EmployeeTransactionsListCreateAPIView

urlpatterns = [
    path("", EmployeeListAPIView.as_view()),
    path("transactions/", include("data.employee.transactions.urls")),
    path(
        "<uuid:employee>/transactions", EmployeeTransactionsListCreateAPIView.as_view()
    ),
]
