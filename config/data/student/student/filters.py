import django_filters as filters

from django.db.models import F


class StudentFilter(filters.FilterSet):
    order_by = filters.CharFilter(method="filter_order_by")

    def filter_order_by(self, queryset, name, value):
        if not value:
            return queryset

        value = value.strip()
        allowed = {
            "created_at",
            "-created_at",
            "active_date",
            "-active_date",
            "balance",
            "-balance",
        }
        if value not in allowed:
            return queryset

        field = value.lstrip("-")
        desc = value.startswith("-")

        order = (
            F(field).desc(nulls_last=True) if desc else F(field).asc(nulls_last=True)
        )
        return queryset.order_by(order, "-id" if desc else "id")
