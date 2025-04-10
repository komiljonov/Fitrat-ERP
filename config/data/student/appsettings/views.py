from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from ...student.course.models import Course
from ...student.student.models import Student
from ...student.studentgroup.models import StudentGroup

from rest_framework.response import Response

from .serializers import StoresSerializer
from .models import Store

from rest_framework.generics import ListCreateAPIView,RetrieveUpdateDestroyAPIView


class StoresListView(ListCreateAPIView):
    queryset = Store.objects.all()
    serializer_class = StoresSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Store.objects.all()

        filial = self.request.query_params.get('filial', None)

        seen = self.request.query_params.get('seen', None)
        if filial:
            queryset = queryset.filter(filial__id=filial)
        if seen:
            queryset = queryset.filter(seen=seen.capitalize())
        return queryset


class StoreDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Store.objects.all()
    serializer_class = StoresSerializer
    permission_classes = [IsAuthenticated]

class StudentHomeView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        
        user = self.request.user

        avg_progress = Student.objects.filter(
            user = user
        )

        in_progress_courses = Course.objects.filter(
            group__in=StudentGroup.objects.filter(
                group__status='ACTIVE', student__user=user
            ).values_list('group', flat=True)
        ).distinct()
        
        in_progress_courses_counts = in_progress_courses.count()


        return Response( {
            "avg_progress" : avg_progress,
            "in_progress_courses" : in_progress_courses,
            "in_progress_courses_counts" : in_progress_courses_counts
        }
        ) 