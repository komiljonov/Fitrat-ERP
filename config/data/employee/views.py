from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from django.utils import timezone

from django.http import Http404


from rest_framework.request import Request
from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
)
from rest_framework import status

from rest_framework.response import Response

from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError

# from data.employee.models import Employee, EmployeeTransaction
from data.employee.filters import EmployeesFilter
from data.employee.models import Employee, EmployeeTransaction
from data.employee.serializers import EmployeeSerializer


from data.employee.transactions.views import (
    EmployeeTransactionsListCreateAPIView as ETLCAV,
    EmployeeTransactionRetrieveDestroyAPIView as ETRDAV,
)
from data.finances.finance.models import Casher
from data.finances.timetracker.hrpulse import HrPulseIntegration
from data.firstlesson.models import FirstLesson
from data.lid.new_lid.models import Lid
from data.student.groups.models import Group, SecondaryGroup
from data.student.student.models import Student


class EmployeeListAPIView(ListCreateAPIView):
    queryset = Employee.objects.select_related("photo")
    filterset_class = EmployeesFilter

    def get_serializer(self, *args, **kwargs):
        kwargs.setdefault("context", self.get_serializer_context())

        if self.request.method == "POST":
            # Creating new employee — do not restrict fields
            return EmployeeSerializer(*args, **kwargs)
        else:
            # Listing employees — limit fields
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


class EmployeeRetrieveAPIView(RetrieveUpdateDestroyAPIView):

    queryset = Employee.objects.select_related("photo")

    serializer_class = EmployeeSerializer


class EmployeeTransactionsListCreateAPIView(ETLCAV):
    """
    GET  /<uuid:employee>/transactions      -> list transactions for that employee
    POST /<uuid:employee>/transactions      -> create a transaction for that employee
    """

    lookup_url_kwarg = "employee"  # from your URLConf

    def get_employee(self) -> Employee:
        pk = self.kwargs[self.lookup_url_kwarg]

        if pk == "me":
            user = self.request.user
            if not user or not user.is_authenticated:
                raise Http404("Employee not found.")

            # assuming request.user *is* the Employee model
            return user

        return get_object_or_404(Employee, pk=pk)

    def get_queryset(self):
        employee = self.get_employee()
        qs = EmployeeTransaction.objects.select_related("employee").filter(
            employee=employee,
            is_archived=False,
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
            employee=employee,
            is_archived=False,
        )

        return qs


class EmployeeArchiveAPIView(APIView):

    lookup_url_kwarg = "pk"  # from your URLConf

    def post(self, request: HttpRequest | Request, pk: str):

        employee = get_object_or_404(Employee, pk=pk)

        if employee.is_archived:
            raise ValidationError("Employee already archived", "already_archived")

        if employee.second_user:
            tt = HrPulseIntegration()

            tt_response = tt.archive_employee(employee.second_user)

            if not tt_response or "error" in tt_response:
                return Response(
                    {"error": "TimeTracker bilan bog'lanib bo'lmadi."},
                    status=status.HTTP_502_BAD_GATEWAY,
                )

        employee.is_archived = True
        employee.archived_at = timezone.now()
        employee.save()

        return Response(
            {
                "ok": True,
                "message": "Xodim arxivlandi!",
            },
            status=status.HTTP_200_OK,
        )


class EmployeeRelatedObjectsAPIView(APIView):

    def get(self, request: HttpRequest, pk: str):

        employee = get_object_or_404(Employee, pk=pk)

        groups = Group.objects.filter(
            teacher=employee,
            is_archived=False,
            status="ACTIVE",
        )

        secondary_groups = SecondaryGroup.objects.filter(
            teacher=employee,
            status="ACTIVE",
            is_archived=False,
        )

        service_orders = Lid.objects.filter(
            service_manager=employee,
            lid_stage_type="ORDERED_LID",
            ordered_stages__in=["KUTULMOQDA", "YANGI_BUYURTMA"],
            is_archived=False,
        )

        sales_orders = Lid.objects.filter(
            sales_manager=employee,
            lid_stage_type="ORDERED_LID",
            ordered_stages__in=["KUTULMOQDA", "YANGI_BUYURTMA"],
            is_archived=False,
        )

        service_first_lessons = FirstLesson.objects.filter(
            lead__service_manager=employee,
            is_archived=False,
        )

        sales_first_lessons = FirstLesson.objects.filter(
            lead__sales_manager=employee,
            is_archived=False,
        )

        service_active_students = Student.objects.filter(
            service_manager=employee,
            is_archived=False,
            student_stage_type="ACTIVE_STUDENT",
        )

        sales_active_students = Student.objects.filter(
            sales_manager=employee,
            is_archived=False,
            student_stage_type="ACTIVE_STUDENT",
        )

        service_new_students = Student.objects.filter(
            service_manager=employee,
            is_archived=False,
            student_stage_type="NEW_STUDENT",
        )

        sales_new_students = Student.objects.filter(
            sales_manager=employee,
            is_archived=False,
            student_stage_type="NEW_STUDENT",
        )

        finance_cashiers = Casher.objects.filter(user=employee, is_archived=False)

        return Response(
            {
                "groups": groups.count(),
                "secondary_groups": secondary_groups.count(),
                "service_orders": service_orders.count(),
                "sales_orders": sales_orders.count(),
                "service_first_lessons": service_first_lessons.count(),
                "sales_first_lessons": sales_first_lessons.count(),
                "service_active_students": service_active_students.count(),
                "sales_active_students": sales_active_students.count(),
                "service_new_students": service_new_students.count(),
                "sales_new_students": sales_new_students.count(),
            }
        )
