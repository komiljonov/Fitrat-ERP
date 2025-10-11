from rest_framework.generics import ListAPIView

from data.student.groups.models import Group


class GroupListAPIView(ListAPIView):

    queryset = Group.objects.all()
    
    
    serializer_class = GroupSerializer
