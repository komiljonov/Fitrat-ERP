import django_filters as filters

from data.student.subject.models import Theme


class ThemeFilter(filters.FilterSet):

    class Meta:
        model = Theme
        fields = ["subject", "course", "level"]
