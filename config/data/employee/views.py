from rest_framework.generics import ListCreateAPIView

from data.employee.models import Employee
from data.account.models import CustomUser
from data.employee.filters import EmployeesFilter
from data.employee.serializers import EmployeeSerializer


class EmployeeListAPIView(ListCreateAPIView):

    queryset = Employee.objects.exclude(role__in=["Student", "Parents"]).select_related(
        "photo"
    )

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
