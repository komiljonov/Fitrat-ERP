from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import ListCreateAPIView, ListAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Student
from .serializers import StudentSerializer, StudentTokenObtainPairSerializer
from ..lesson.models import Lesson
from ..lesson.serializers import LessonSerializer
from ..studentgroup.models import StudentGroup
from ...account.permission import FilialRestrictedQuerySetMixin


class StudentListView(FilialRestrictedQuerySetMixin, ListCreateAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [IsAuthenticated]

    filter_backends = (DjangoFilterBackend, OrderingFilter, SearchFilter)

    search_fields = ('first_name', 'last_name', 'phone')

    ordering_fields = ('student_stage_type', 'is_archived', 'moderator',
                                                            'marketing_channel', 'filial')

    filterset_fields = ('student_stage_type', 'is_archived',
                        'moderator', 'marketing_channel', 'filial')

    def get_queryset(self):
        """
        Customize queryset filtering based on user roles and other criteria.
        """
        user = self.request.user

        queryset = super().get_queryset()

        # Additional role-based filtering
        if hasattr(user, "role"):
            if user.role == "CALL_OPERATOR":
                queryset = queryset.none()
            elif user.role == "ADMINISTRATOR":
                queryset = queryset.filter(filial=user.filial)

        return queryset





class StudentLoginAPIView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = StudentTokenObtainPairSerializer(data=request.data)

        if serializer.is_valid():
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class StudentDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [IsAuthenticated]

class StudentListNoPG(FilialRestrictedQuerySetMixin,ListAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [IsAuthenticated]

    def get_paginated_response(self, data):
        return Response(data)



class StudentScheduleView(FilialRestrictedQuerySetMixin,ListAPIView):
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        student_groups = StudentGroup.objects.filter(student_id=self.kwargs['pk']).values_list('group_id', flat=True)
        return Lesson.objects.filter(group_id__in=student_groups).order_by("day", "start_time")

