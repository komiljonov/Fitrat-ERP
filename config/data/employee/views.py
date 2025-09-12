from django.shortcuts import get_object_or_404
from rest_framework.generics import ListCreateAPIView
from rest_framework.exceptions import ValidationError

from data.employee.models import Employee, EmployeeTransaction
from data.employee.filters import EmployeesFilter
from data.employee.serializers import EmployeeSerializer


from data.employee.transactions.views import (
    EmployeeTransactionsListCreateAPIView as ETLCAV,
    EmployeeTransactionRetrieveDestroyAPIView as ETRDAV,
)


class EmployeeListAPIView(ListCreateAPIView):

    queryset = Employee.objects.select_related("photo")

    filterset_class = EmployeesFilter

    def get_serializer(self, *args, **kwargs):

        kwargs.setdefault("context", self.get_serializer_context())
        return EmployeeSerializer(
            *args,
            **kwargs,
            include_only=[
                "id",
                "first_name",
                "last_name",
                "full_name",
                "phone",
                "balance",
                "photo",
                "monitoring",
                "role",
                "calculate_penalties",
                "created_at",
            ],
        )


class EmployeeTransactionsListCreateAPIView(ETLCAV):
    """
    GET  /<uuid:employee>/transactions      -> list transactions for that employee
    POST /<uuid:employee>/transactions      -> create a transaction for that employee
    """

    lookup_url_kwarg = "employee"  # from your URLConf

    def get_employee(self) -> Employee:
        return get_object_or_404(Employee, pk=self.kwargs[self.lookup_url_kwarg])

    def get_queryset(self):
        employee = self.get_employee()
        qs = EmployeeTransaction.objects.select_related("employee").filter(
            employee=employee
        )

        return qs

    def perform_create(self, serializer):
        url_employee = self.get_employee()

        # If the payload included an employee, ensure it matches the URL
        payload_employee = serializer.validated_data.get("employee")
        if payload_employee and payload_employee.pk != url_employee.pk:
            raise ValidationError({"employee": "Must match the employee in the URL."})

        serializer.save(employee=url_employee)


class EmployeeTransactionRetrieveDestroyAPIView(ETRDAV):

    lookup_url_kwarg = "employee"  # from your URLConf

    def get_employee(self) -> Employee:
        return get_object_or_404(Employee, pk=self.kwargs[self.lookup_url_kwarg])

    def get_queryset(self):
        employee = self.get_employee()
        qs = EmployeeTransaction.objects.select_related("employee").filter(
            employee=employee
        )

        return qs
