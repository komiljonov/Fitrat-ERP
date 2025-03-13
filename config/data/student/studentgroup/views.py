import datetime

from django.db.models import OuterRef, Exists, Q
from django.utils.timezone import now
from django_filters.rest_framework import DjangoFilterBackend
from icecream import ic
from rest_framework import status
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, ListAPIView, get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import StudentGroup, SecondaryStudentGroup
from .serializers import StudentsGroupSerializer, SecondaryStudentsGroupSerializer
from ..attendance.models import Attendance
from ..attendance.serializers import AttendanceSerializer
from ..groups.models import SecondaryGroup, Group
from ..groups.serializers import SecondarygroupModelSerializer


class StudentsGroupList(ListCreateAPIView):
    queryset = StudentGroup.objects.all()
    serializer_class = StudentsGroupSerializer
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)

    search_fields = (
        'group__name', 'student__first_name', 'lid__first_name', 'student__last_name', 'lid__last_name',
        'group__status',
        'group__teacher__id'
    )
    filter_fields = filterset_fields = search_fields

    def get_queryset(self):
        today = datetime.date.today()
        user = self.request.user

        if user.role == 'TEACHER':
            queryset = StudentGroup.objects.filter(group__teacher__id=user.id)
        else:
            queryset = StudentGroup.objects.filter(group__filial__in=user.filial.all())

        # **Exclude students who have attended today**
        attended_today = Attendance.objects.filter(
            student=OuterRef("student"),  # Ensure this matches your Attendance model field
            group=OuterRef("group"),
            created_at__date=today
        )

        # Apply filters
        queryset = queryset.annotate(
            has_attended_today=Exists(attended_today)
        ).filter(
            has_attended_today=False,  # Exclude students who attended today
            lid__isnull=False  # Exclude null `lid`
        )

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
        Fetch students related to a specific group, filtering based on attendance reason and date.
        """
        group_id = self.kwargs.get('pk')
        reason = self.request.query_params.get('reason', None)

        # Get today's date for filtering attendance records
        today = now().date()
        start_of_day = datetime.datetime.combine(today, datetime.time.min)
        end_of_day = datetime.datetime.combine(today, datetime.time.max)

        queryset = StudentGroup.objects.filter(group__id=group_id)

        if reason == "1":  # Students who were present today
            present_attendance = Attendance.objects.filter(
                group_id=group_id,
                reason="IS_PRESENT",
                lid__isnull=True,
                created_at__gte=start_of_day,
                created_at__lte=end_of_day
            ).values_list('student_id', 'lid_id', flat=False)  # Get student & lid IDs

        elif reason == "0":  # Students who were absent today (REASONED/UNREASONED)
            present_attendance = Attendance.objects.filter(
                group_id=group_id,
                reason__in=["UNREASONED", "REASONED"],
                lid__isnull=True,
                created_at__gte=start_of_day,
                created_at__lte=end_of_day
            ).values_list('student_id', 'lid_id', flat=False)

        else:
            return queryset  # Return all students in the group if no reason is provided

        # Filter StudentGroup based on student & lid attendance
        student_ids = {entry[0] for entry in present_attendance if entry[0] is not None}
        lid_ids = {entry[1] for entry in present_attendance if entry[1] is not None}

        queryset = queryset.filter(Q(student__id__in=student_ids) | Q(lid__id__in=lid_ids))

        return queryset

    def get_paginated_response(self, data):
        """
        Returns paginated response if pagination is enabled, otherwise returns all data.
        """
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

        ic(group_id)

        filters = Q(student__id=student_id)
        if hasattr(StudentGroup, "lid"):
            filters |= Q(lid__id=student_id)

        student = StudentGroup.objects.filter(group__id=group_id).filter(filters).first()
        attendance = Attendance.objects.filter(group__id=group_id).filter(filters).first()
        ic(student)

        if student:
            attendance.delete()
            student.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response({"error": "Student not found"}, status=status.HTTP_404_NOT_FOUND)


class SecondaryStudentGroupDelete(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        student_id = self.kwargs.get("pk")
        group_id = self.request.query_params.get("group")

        if not student_id or not group_id:
            return Response({"error": "Missing student or group ID"}, status=status.HTTP_400_BAD_REQUEST)

        ic(group_id)

        filters = Q(student__id=student_id)
        if hasattr(SecondaryStudentGroup, "lid"):
            filters |= Q(lid__id=student_id)

        student = SecondaryStudentGroup.objects.filter(group__id=group_id).filter(filters).first()
        ic(student)

        if student:
            student.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response({"error": "Student not found"}, status=status.HTTP_404_NOT_FOUND)


class GroupStudentStatistics(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk, **kwargs):
        group = get_object_or_404(Group, pk=pk)

        # Get total students in the group
        students = StudentGroup.objects.filter(group=group).count()

        # Get today's start and end time
        today = now().date()
        start_of_day = datetime.datetime.combine(today, datetime.time.min)
        end_of_day = datetime.datetime.combine(today, datetime.time.max)

        # Get attendance statistics
        is_attendanded = Attendance.objects.filter(
            group=group,
            created_at__gte=start_of_day,
            created_at__lte=end_of_day,
            reason="IS_PRESENT"
        ).count()

        is_absent = Attendance.objects.filter(
            group=group,
            reason__in=["REASONED", "UNREASONED"],
            created_at__gte=start_of_day,
            created_at__lte=end_of_day
        ).count()

        # Calculate attendance percentages
        percentage_is_attendanded = (is_attendanded / students * 100) if students > 0 else 0
        percentage_is_apcent = (is_absent / students * 100) if students > 0 else 0

        return Response({
            "students": students,
            "is_attendant": is_attendanded,
            "is_absent": is_absent,
            "percentage_is_attendant": round(percentage_is_attendanded, 2),
            "percentage_is_absent": round(percentage_is_apcent, 2),
        })


class GroupAttendedStudents(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AttendanceSerializer

    def get_queryset(self):
        group_id = self.kwargs.get('pk')

        group = Group.objects.get(id=group_id)

        reason = self.request.query_params.get("reason")
        filial = self.request.query_params.get("filial")


        queryset =  Attendance.objects.filter(
            group=group,
            created_at__gte=datetime.date.today()
        )

        ic(reason)

        if reason and reason == "1":
            queryset = queryset.filter(
                reason="IS_PRESENT"
            )
        if reason and reason == "0":
            queryset = queryset.filter(
                reason__in = [
                    "REASONED","UNREASONED"
                ]
            )
        return queryset


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


class StudentGroupStatistics(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, **kwargs):
        filial = self.request.query_params.get("filial")
        course = self.request.query_params.get("course")
        teacher = self.request.query_params.get("teacher")

        all = StudentGroup.objects.filter(filial__id=filial)
        orders = StudentGroup.objects.filter(filial__id=filial, lid__lid_stage_type="ORDERED_LID")
        students = StudentGroup.objects.filter(filial__id=filial, student__isnull=False)

        if course:
            all = all.filter(group__course__id=course)
            orders = orders.filter(group__course__id=course)
            students = students.filter(group__course__id=course)

        if teacher:
            all = all.filter(group__teacher__id=teacher)
            orders = orders.filter(group__teacher__id=teacher)
            students = students.filter(group__teacher__id=teacher)

        return Response({
            "all" : all.count(),
            "students" : students.count(),
            "orders" : orders.count(),
        })
