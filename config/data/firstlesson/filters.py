import django_filters as filters

from django_filters.widgets import RangeWidget

from data.department.filial.models import Filial
from data.department.marketing_channel.models import MarketingChannel
from data.employee.models import Employee
from data.firstlesson.models import FirstLesson
from data.student.course.models import Course
from data.student.subject.models import Subject


class FirstLessonsFilter(filters.FilterSet):

    filial = filters.ModelChoiceFilter(queryset=Filial.objects.all())

    status = filters.ChoiceFilter(choices=FirstLesson._meta.get_field("status").choices)

    operator = filters.ModelChoiceFilter(
        field_name="lead__call_operator",
        queryset=Employee.objects.filter(role="CALL_OPERATOR"),
    )

    sales_manager = filters.ModelChoiceFilter(
        field_name="lead__sales_operator",
        queryset=Employee.objects.filter(role="ADMINISTRATOR"),
    )

    subject = filters.ModelChoiceFilter(queryset=Subject.objects.all())
    course = filters.ModelChoiceFilter(queryset=Course.objects.all())

    marketing_channel = filters.ModelChoiceFilter(
        queryset=MarketingChannel.objects.all()
    )

    teacher = filters.ModelChoiceFilter(
        field_name="group__teacher", queryset=Employee.objects.filter(role="TEACHER")
    )

    created_at = filters.DateFromToRangeFilter(
        field_name="created_at",
        widget=RangeWidget(
            attrs={"placeholder": "YYYY-MM-DD", "suffixes": ["start", "end"]}
        ),
    )

    class Meta:
        model = FirstLesson
        fields = [
            "filial",
            "status",
            "operator",
            "sales_manager",
            "subject",
            "course",
            "marketing_channel",
            "teacher",
            "created_at",
        ]
