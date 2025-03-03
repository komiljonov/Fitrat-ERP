import datetime

from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from icecream import ic
from rest_framework import status
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, ListAPIView, get_object_or_404, \
    CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import StudentGroup, SecondaryStudentGroup
from .serializers import StudentsGroupSerializer, SecondaryStudentsGroupSerializer
from ..attendance.models import Attendance
from ..attendance.serializers import AttendanceSerializer
from ..groups.models import SecondaryGroup, Group
from ..groups.serializers import SecondaryGroupSerializer, SecondarygroupModelSerializer


class StudentsGroupList(ListCreateAPIView):
    queryset = StudentGroup.objects.all()
    serializer_class = StudentsGroupSerializer
    # permission_classes = [IsAuthenticated]

    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    search_fields = (
    'group__name', 'student__first_name', 'lid__first_name', 'student__last_name', 'lid__last_name', 'group__status',
    'group__teacher__id')
    filter_fields = (
    'group__name', 'student__first_name', 'lid__first_name', 'student__last_name', 'lid__last_name', 'group__status',
    'group__teacher__id')
    filterset_fields = (
    'group__name', 'student__first_name', 'lid__first_name', 'student__last_name', 'lid__last_name', 'group__status',
    'group__teacher__id')

    def get_queryset(self):

        if self.request.user.role == 'TEACHER':
            queryset = StudentGroup.objects.filter(group__teacher__id=self.request.user.id)
            return queryset
        else:
            queryset = StudentGroup.objects.filter(group__filial__in=self.request.user.filial.all())
            ic(self.request.user.filial.all())
            ic(queryset)
            return queryset


class StudentGroupDetail(RetrieveUpdateDestroyAPIView):
    queryset = StudentGroup.objects.all()
    serializer_class = StudentsGroupSerializer
    permission_classes = [IsAuthenticated]


class StudentGroupNopg(ListAPIView):
    queryset = StudentGroup.objects.all()
    serializer_class = StudentsGroupSerializer
    permission_classes = [IsAuthenticated]

    def get_paginated_response(self, data):
        return Response(data)
    def get_queryset(self):
        if self.request.user.role == 'TEACHER':
            queryset = StudentGroup.objects.filter(group__teacher__id=self.request.user.id)
            return queryset
        else:
            queryset = StudentGroup.objects.filter(group__filial__in=self.request.user.filial.all())
            return queryset


class GroupStudentList(ListAPIView):
    serializer_class = StudentsGroupSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Fetch the students related to a specific group from the URL path parameter.
        """
        group_id = self.kwargs.get('pk')
        queryset = StudentGroup.objects.filter(group__id=group_id)

        return queryset

    def get_paginated_response(self, data):
        return Response(data)


class SecondaryGroupStudentList(ListAPIView):
    serializer_class = SecondaryStudentsGroupSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Fetch the students related to a specific group from the URL path parameter.
        """
        group_id = self.kwargs.get('pk')
        queryset = SecondaryStudentGroup.objects.filter(group__id=group_id)

        return queryset

    def get_paginated_response(self, data):
        return Response(data)



class StudentGroupDelete(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        student_id = self.kwargs.get("pk")
        group_id = self.request.query_params.get("group")

        if not student_id or not group_id:
            return Response({"error": "Missing student or group ID"}, status=status.HTTP_400_BAD_REQUEST)

        # Convert group_id to integer safely
        try:
            group_id = int(group_id)
        except (ValueError, TypeError):
            return Response({"error": "Invalid group ID"}, status=status.HTTP_400_BAD_REQUEST)

        # Construct filter dynamically
        filters = Q(student__id=student_id)
        if hasattr(StudentGroup, "lid"):
            filters |= Q(lid__id=student_id)

        student = StudentGroup.objects.filter(group__id=group_id).filter(filters).first()

        if student:
            student.delete()
            return Response({"message": "Student removed successfully"}, status=status.HTTP_204_NO_CONTENT)

        return Response({"error": "Student not found"}, status=status.HTTP_404_NOT_FOUND)



class GroupStudentStatistics(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk,**kwargs):
        group = Group.objects.get(pk=pk)
        if group:
            students = StudentGroup.objects.filter(group=group).count()
            is_attendanded = Attendance.objects.filter(group=group, created_at__gte=datetime.datetime.today(),reason="IS_PRESENT",created_at__lte=datetime.datetime.today()
                                                                                        + datetime.timedelta(days=1)).count()
            is_apcent = Attendance.objects.filter(group=group, reason__in=["REASONED","UNREASONED"],created_at__gte=datetime.datetime.today(),
                                                  created_at__lte=datetime.datetime.today() + datetime.timedelta(days=1) ).count()
            persentage_is_attendanded = students /100 * is_attendanded
            persentage_is_apcent = is_apcent /100 * is_apcent

            return Response({
                "students": students,
                'is_attendant': is_attendanded,
                'is_absent': is_apcent,
                'percentage_is_attendant': persentage_is_attendanded,
                'percentage_is_absent': persentage_is_apcent,
            })


class GroupAttendedStudents(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AttendanceSerializer

    def get_queryset(self):
        group_id = self.kwargs.get('pk')
        group = Group.objects.get(id=group_id)

        return Attendance.objects.filter(
            group=group,
            created_at__gte=datetime.date.today()
        )
    def get_paginated_response(self, data):
        return Response(data)



class GroupStudentDetail(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = StudentsGroupSerializer

    def get_queryset(self):
        id = self.kwargs.get('pk')
        print(id)

        return StudentGroup.objects.filter(Q(student=id) | Q(lid=id))


class SecondaryStudentList(ListCreateAPIView):
    serializer_class = SecondaryStudentsGroupSerializer
    queryset = SecondaryStudentGroup.objects.all()
    permission_classes = [IsAuthenticated]


    def get_queryset(self):
        if self.request.user.role == 'ASSISTANT':
            return SecondaryStudentGroup.objects.filter(group__teacher__id=self.request.user.id)
        return SecondaryStudentGroup.objects.filter(group__filial__in=self.request.user.filial.all())


class SecondaryGroupList(ListAPIView):
    serializer_class = SecondarygroupModelSerializer
    queryset = SecondaryGroup.objects.all()  # Corrected to fetch data
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        id = self.kwargs.get('pk')
        if id:
            return SecondaryGroup.objects.filter(teacher__id=id)
        return SecondaryGroup.objects.none()

    def get_paginated_response(self, data):
        return Response(data)

