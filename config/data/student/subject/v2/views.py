from rest_framework.generics import ListAPIView

from data.student.subject.models import Theme
from data.student.subject.serializers import ThemeSerializer
from data.student.subject.v2.filters import ThemeFilter


class ThemeNoPgListAPIView(ListAPIView):

    serializer_class = ThemeSerializer.only("id", "title", "description")
    pagination_class = None

    queryset = Theme.objects.filter(is_archived=False)

    filterset_class = ThemeFilter
