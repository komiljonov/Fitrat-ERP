from rest_framework.generics import ListAPIView

from data.student.groups.models import Group
from data.student.groups.v2.serializers import GroupSerializer


class GroupListAPIView(ListAPIView):

    queryset = Group.objects.select_related("start_theme")

    serializer_class = GroupSerializer
