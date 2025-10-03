import django_filters as filters
from django.db.models import Q

from data.department.filial.models import Filial
from data.employee.models import Employee
from data.student.course.models import Course
from data.student.student.models import Student
from data.student.subject.models import Subject


class StudentFilter(filters.FilterSet):

    filial = filters.ModelChoiceFilter(queryset=Filial.objects.all())

    lang = filters.CharFilter(field_name="education_lang")

    subject = filters.ModelChoiceFilter(queryset=Subject.objects.all())

    course = filters.ModelChoiceFilter(queryset=Course.objects.all())

    operator = filters.ModelChoiceFilter(
        queryset=Employee.objects.filter(
            Q(role="CALL_OPERATOR") | Q(is_call_center=True)
        ),
        field_name="call_operator",
    )

    sales_manager = filters.ModelChoiceFilter(
        queryset=Employee.objects.filter(role="ADMINISTRATOR"),
        field_name="sales_manager",
    )

    service_manager = filters.ModelChoiceFilter(
        queryset=Employee.objects.filter(
            Q(role="SERVICE_MANAGER") | Q(is_service_manager=True)
        ),
        field_name="service_manager",
    )

    teacher = filters.ModelChoiceFilter(
        queryset=Employee.objects.all(),
        method="filter_teacher",
    )

    balance = filters.NumericRangeFilter(method="filter_balance")

    class Meta:
        model = Student
        fields = [
            "filial",
            "lang",
            "subject",
            "course",
            "operator",
            "sales_manager",
            "service_manager",
            "teacher",
            "balance",
        ]

    def filter_teacher(self, qs, name, value):
        return qs.filter(groups__teacher=value)

    def filter_balance(self, qs, name, value):
        if not value:
            return qs

        q = Q()

        if value.start is not None:
            q &= Q(balance__gte=value.start)
        if value.stop is not None:
            q &= Q(balance__lte=value.stop)

        return qs.filter(q).distinct()
