import django_filters as filters

from django.db.models import Case, When, Value, IntegerField, Q
from datetime import datetime, time, timedelta


from django.utils import timezone


from data.department.filial.models import Filial
from data.department.marketing_channel.models import MarketingChannel
from data.employee.models import Employee
from data.firstlesson.models import FirstLesson
from data.student.course.models import Course
from data.student.subject.models import Subject


class FirstLessonsFilter(filters.FilterSet):

    q = filters.CharFilter(method="search")

    filial = filters.ModelChoiceFilter(queryset=Filial.objects.all())

    status = filters.ChoiceFilter(choices=FirstLesson._meta.get_field("status").choices)

    operator = filters.ModelChoiceFilter(
        field_name="lead__call_operator",
        queryset=Employee.objects.filter(role="CALL_OPERATOR"),
    )

    sales_manager = filters.ModelChoiceFilter(
        field_name="lead__sales_manager",
        queryset=Employee.objects.filter(role="ADMINISTRATOR"),
    )

    service_manager = filters.ModelChoiceFilter(
        field_name="lead__service_manager",
        queryset=Employee.objects.filter(role="SERVICE_MANAGER"),
    )

    subject = filters.ModelChoiceFilter(queryset=Subject.objects.all())
    course = filters.ModelChoiceFilter(queryset=Course.objects.all())

    marketing_channel = filters.ModelChoiceFilter(
        field_name="lead__marketing_channel",
        queryset=MarketingChannel.objects.all(),
    )

    teacher = filters.ModelChoiceFilter(
        field_name="group__teacher", queryset=Employee.objects.filter(role="TEACHER")
    )

    created_at_start = filters.CharFilter(method="filter_created_at_range")
    created_at_end = filters.CharFilter(method="filter_created_at_range")

    created_at = filters.DateTimeFromToRangeFilter(field_name="created_at")

    order_by = filters.CharFilter(method="filter_order_by")

    class Meta:
        model = FirstLesson
        fields = [
            "filial",
            "status",
            "operator",
            "sales_manager",
            "service_manager",
            "subject",
            "course",
            "marketing_channel",
            "teacher",
            "created_at",
            "q",
        ]

    def filter_order_by(self, qs, name, value):
        if not value:
            return qs

        value = value.strip()
        allowed = {
            "balance",
            "-balance",
            "created_at",
            "-created_at",
            "date",
            "-date",
            "status",
            "-status",
        }

        if value not in allowed:
            return qs

        if "balance" in value:
            direction = "-" if value.startswith("-") else ""
            qs = qs.order_by(f"{direction}balance")

        elif "created_at" in value or "date" in value:
            qs = qs.order_by(value)

        elif "status" in value:
            direction = "-" if value.startswith("-") else ""
            # Keep only PENDING and DIDNTCOME in order
            order = ["PENDING", "DIDNTCOME"]
            # Exclude CAME entirely
            qs = (
                qs.exclude(status="CAME")
                .annotate(
                    _status_order=Case(
                        *[When(status=s, then=Value(i)) for i, s in enumerate(order)],
                        default=Value(len(order)),
                        output_field=IntegerField(),
                    )
                )
                .order_by(f"{direction}_status_order")
            )

        return qs

    def _parse_date(self, s: str):
        try:
            return datetime.strptime(s, "%Y-%m-%d").date()
        except Exception:
            return None

    def filter_created_at_range(self, qs, name, value):
        start_str = self.data.get("created_at_start")
        end_str = self.data.get("created_at_end")

        if start_str:
            d = self._parse_date(start_str)
            if d:
                start_dt = datetime.combine(d, time.min)
                qs = qs.filter(created_at__gte=start_dt)

        if end_str:
            d = self._parse_date(end_str)
            if d:
                # end is exclusive: < next day 00:00
                end_dt = datetime.combine(d + timedelta(days=1), time.min)
                qs = qs.filter(created_at__lt=end_dt)

        return qs

    def search(self, qs, name, value):

        if not value:
            return value

        return qs.filter(
            Q(lead__first_name__icontains=value)
            | Q(lead__last_name__icontains=value)
            | Q(lead__middle_name__icontains=value)
            | Q(lead__phone_number__icontains=value)
            | Q(group__name__icontains=value)
        )
