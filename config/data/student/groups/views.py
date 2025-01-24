
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.generics import ListAPIView, ListCreateAPIView,RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Group
from .serializers import GroupSerializer, GroupLessonSerializer


class StudentGroupsView(ListCreateAPIView):
    queryset = Group.objects.all()
    # permission_classes = [IsAuthenticated]
    serializer_class = GroupSerializer
    filter_backends = (DjangoFilterBackend,OrderingFilter,SearchFilter)
    search_fields = ('name','scheduled_day_type__name')
    ordering_fields = ('name','scheduled_day_type','start_date','end_date','price_type')
    filterset_fields = ('name','scheduled_day_type__name','price_type')



class StudentRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Group.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = GroupSerializer

class StudentListAPIView(ListAPIView):
    queryset = Group.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = GroupSerializer

    def get_paginated_response(self, data):
        return Response(data)



class GroupLessonScheduleView(APIView):
    """
    API endpoint to get the lesson schedule for a given group ID.
    """
    def get(self, request, **kwargs):
        try:
            # Fetch the group by ID
            group = Group.objects.get(id=kwargs.get('pk'))
            # Serialize the group with the lesson schedule
            serializer = GroupLessonSerializer(group)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Group.DoesNotExist:
            # Return a 404 response if the group is not found
            return Response(
                {"error": "Group not found."},
                status=status.HTTP_404_NOT_FOUND
            )
