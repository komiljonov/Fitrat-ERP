import django_filters as filters

from django.db.models import Q
from django.db.models.functions import Coalesce

from data.archive.models import Archive
from data.department.filial.models import Filial
from data.employee.models import Employee
from data.student.subject.models import Subject


class ArchiveFilter(filters.FilterSet):
    # map non-Archive fields through related FKs (student/lead)

    q = filters.CharFilter(method="search")

    filial = filters.ModelChoiceFilter(
        queryset=Filial.objects.all(),
        method="filter_filial",
    )

    lang = filters.CharFilter(method="filter_lang")

    subject = filters.ModelChoiceFilter(
        queryset=Subject.objects.all(),
        method="filter_subject",
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

    created_at = filters.DateTimeFromToRangeFilter(field_name="created_at")

    only = filters.CharFilter(method="filter_only")

    order_by = filters.CharFilter(method="filter_order_by")

    class Meta:
        model = Archive
        fields = [
            "q",
            "lang",
            "subject",
            "operator",
            "sales_manager",
            "service_manager",
            "balance",
            "created_at",
            "only",
            "order_by",
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

    def filter_filial(self, qs, name, value):
        return self._either(qs, "filial", value)

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

    def filter_only(self, qs, name, value):
        if not value:
            return qs

        v = str(value).upper()
        mapping = {
            "LEADS": Q(lead__lid_stage_type="NEW_LID"),
            "ORDERS": Q(lead__lid_stage_type="ORDERED_LID"),
            "NEW_STUDENTS": Q(student__student_stage_type="NEW_STUDENT"),
            "ACTIVE_STUDENTS": Q(student__student_stage_type="ACTIVE_STUDENT"),
            "ENTITLED": Q(lead__balance__gt=0) | Q(student__balance__gt=0),
            "INDEBTED": Q(lead__balance__lt=0) | Q(student__balance__lt=0),
        }

        cond = mapping.get(v)
        if not cond:
            return qs
        return qs.filter(cond).distinct()

    def filter_order_by(self, qs, name, value):

        if not value:
            return qs

        value = value.strip()
        allowed = {"balance", "-balance", "created_at", "-created_at"}

        if value not in allowed:
            return qs

        if "balance" in value:
            direction = "-" if value.startswith("-") else ""
            # Sort by student or lead balance (whichever exists)
            qs = qs.annotate(
                _balance=Coalesce("lead__balance", "student__balance")
            ).order_by(
                f"{direction}_balance",
            )
        elif "created_at" in value:
            qs = qs.order_by(value)

        return qs

    def search(self, qs, name, value):

        if not value:
            return value

        return qs.filter(
            # Search by lead
            Q(lead__first_name__icontains=value)
            | Q(lead__last_name__icontains=value)
            | Q(lead__middle_name__icontains=value)
            | Q(lead__phone_number__icontains=value)
            # Search by students
            | Q(student__first_name__icontains=value)
            | Q(student__last_name__icontains=value)
            | Q(student__middle_name__icontains=value)
            | Q(student__phone__icontains=value)
            # Search by metadata
            | Q(reason__icontains=value)
            # Search by creator
            | Q(creator__full_name__icontains=value)
        )


# education_lang
