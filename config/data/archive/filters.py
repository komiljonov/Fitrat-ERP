import django_filters as filters

from django.db.models import Q

from data.archive.models import Archive
from data.employee.models import Employee
from data.student.subject.models import Subject


class ArchiveFilter(filters.FilterSet):
    # map non-Archive fields through related FKs (student/lead)
    lang = filters.CharFilter(method="filter_lang")

    subject = filters.ModelChoiceFilter(
        queryset=Subject.objects.all(), method="filter_subject"
    )

    operator = filters.ModelChoiceFilter(
        queryset=Employee.objects.filter(
            Q(role="CALL_OPERATOR") | Q(is_call_center=True)
        ),
        method="filter_operator",
    )
    sales_manager = filters.ModelChoiceFilter(
        queryset=Employee.objects.filter(role="ADMINISTRATOR"),
        method="filter_sales_manager",
    )
    service_manager = filters.ModelChoiceFilter(
        queryset=Employee.objects.filter(
            Q(role="SERVICE_MANAGER") | Q(is_service_manager=True)
        ),
        method="filter_service_manager",
    )

    balance = filters.NumericRangeFilter(method="filter_balance")

    created_at = filters.DateTimeFromToRangeFilter(
        field_name="created_at"
    )  # Archive's own field

    class Meta:
        model = Archive
        fields = [
            "lang",
            "subject",
            "operator",
            "sales_manager",
            "service_manager",
            "balance",
            "created_at",
        ]

    # --- helpers ---
    def _either(self, qs, field: str, value):
        """Apply filter to student__{field} OR lead__{field}."""
        if value in (None, ""):
            return qs
        return qs.filter(
            Q(**{f"student__{field}": value}) | Q(**{f"lead__{field}": value})
        ).distinct()

    # --- per-field methods ---
    def filter_lang(self, qs, name, value):
        return self._either(qs, "education_lang", value)

    def filter_subject(self, qs, name, value):
        return self._either(qs, "subject", value)

    def filter_operator(self, qs, name, value):
        return self._either(qs, "call_operator", value)

    def filter_sales_manager(self, qs, name, value):
        return self._either(qs, "sales_manager", value)

    def filter_service_manager(self, qs, name, value):
        return self._either(qs, "service_manager", value)

    def filter_balance(self, qs, name, value):
        if not value:
            return qs
        q = Q()
        if value.start is not None:
            q &= Q(student__balance__gte=value.start) | Q(
                lead__balance__gte=value.start
            )
        if value.stop is not None:
            q &= Q(student__balance__lte=value.stop) | Q(lead__balance__lte=value.stop)
        return qs.filter(q).distinct()


# education_lang
