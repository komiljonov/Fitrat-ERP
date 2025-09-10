import django_filters as filters
from django.db.models import Q

from data.account.models import CustomUser


class EmployeesFilter(filters.FilterSet):

    search = filters.CharFilter(method="filter_search")

    filial = filters.UUIDFilter(field_name="filial_id")

    subject = filters.UUIDFilter(field_name="teachers__subject_id")

    role = filters.CharFilter(field_name="role")

    is_archived = filters.BooleanFilter(field_name="is_archived")

    class Meta:
        model = CustomUser
        fields = ["search", "filial", "subject", "role", "is_archived"]

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(full_name__icontains=value) | Q(phone__icontains=value)
        )
