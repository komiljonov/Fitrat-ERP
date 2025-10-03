from logging import Filter
import django_filters as filters
from django.db.models import Q


class StudentFilter(filters.FilterSet):

    filial = filters.ModelChoiceFilter(queryset=Filter.objects.all())
