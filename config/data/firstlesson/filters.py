import django_filters as filters

from data.department.filial.models import Filial
from data.firstlesson.models import FirstLesson


class FirstLessonsFilter(filters.FilterSet):

    filial = filters.ModelChoiceFilter(queryset=Filial.objects.all())

    status = filters.ChoiceFilter(choices=FirstLesson._meta.get_field("status").choices)

    class Meta:
        model = FirstLesson
        fields = ["filial", "status"]
