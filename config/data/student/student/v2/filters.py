import django_filters as filters
from django.db.models import Q

from data.department.filial.models import Filial


class StudentFilter(filters.FilterSet):

    filial = filters.ModelChoiceFilter(queryset=Filial.objects.all())
