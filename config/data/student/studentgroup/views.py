import datetime

from django.db.models import OuterRef, Exists, Q
from django.utils.timezone import now
from django_filters.rest_framework import DjangoFilterBackend
from icecream import ic
from rest_framework import status
from rest_framework.exceptions import ValidationError, NotFound
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, ListAPIView, get_object_or_404, \
    UpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import StudentGroup, SecondaryStudentGroup
from .serializers import StudentsGroupSerializer, SecondaryStudentsGroupSerializer
from ..attendance.models import Attendance
from ..attendance.serializers import AttendanceSerializer
from ..groups.models import SecondaryGroup, Group
from ..groups.serializers import SecondaryGroupModelSerializer


class StudentsGroupList(ListCreateAPIView):
    queryset = StudentGroup.objects.all()
    serializer_class = StudentsGroupSerializer
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)

    search_fields = (
        'group__name',
        'student__first_name',
        'lid__first_name',
        'student__last_name',
        'lid__last_name',
        'group__status',
        'group__teacher__id'
    )
    filter_fields = filterset_fields = search_fields

    def get_queryset(self):
        status = self.request.query_params.get('status')
        today = datetime.date.today()
        user = self.request.user
        is_archived = self.request.GET.get('is_archived', False)

        if user.role == 'TEACHER':
            queryset = StudentGroup.objects.filter(group__teacher__id=user.id)
        else:
            queryset = StudentGroup.objects.filter(group__filial__in=user.filial.all())
        if status:
            queryset = queryset.filter(group__status=status)

        if is_archived:
            queryset = queryset.filter(is_archived=is_archived.capitalize())

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

        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(student__first_name__icontains=search) |
                Q(lid__first_name__icontains=search) |
                Q(student__last_name__icontains=search) |
                Q(lid__last_name__icontains=search)
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
    pagination_class = None

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

        status = self.request.query_params.get('status')
        is_archived = self.request.GET.get('is_archived', False)

        print(is_archived)

        today = now().date()
        start_of_day = datetime.datetime.combine(today, datetime.time.min)
        end_of_day = datetime.datetime.combine(today, datetime.time.max)

        queryset = StudentGroup.objects.filter(group__id=group_id)

        if is_archived:
            queryset = queryset.filter(Q(student__is_archived=is_archived.capitalize()) | Q(lid__is_archived=is_archived.capitalize())).distinct("id")

        if status:
            queryset = queryset.filter(student__student_stage_type=status)

        if reason == "1":

            present_attendance = Attendance.objects.filter(
                group_id=group_id,
                reason="IS_PRESENT",
                lid__isnull=True,
                created_at__gte=start_of_day,
                created_at__lte=end_of_day
            ).values_list('student_id', 'lid_id', flat=False)

        elif reason == "0":
            present_attendance = Attendance.objects.filter(
                group_id=group_id,
                reason__in=["UNREASONED", "REASONED"],
                lid__isnull=True,
                created_at__gte=start_of_day,
                created_at__lte=end_of_day
            ).values_list('student_id', 'lid_id', flat=False)

        else:
            return queryset

        student_ids = {entry[0] for entry in present_attendance if entry[0] is not None}
        lid_ids = {entry[1] for entry in present_attendance if entry[1] is not None}

        queryset = queryset.filter(Q(student__id__in=student_ids) | Q(lid__id__in=lid_ids))

        print(list(queryset.distinct()))

        return queryset

    def get_paginated_response(self, data):
        seen = set()
        unique_data = []
        for item in data:
            item_id = item.get('id')
            if item_id not in seen:
                seen.add(item_id)
                unique_data.append(item)
        return Response(unique_data)


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


class SecondaryGroupUpdate(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, *args, **kwargs):
        student_id = self.kwargs.get('student_id')
        group_id = request.GET.get('group_id')
        new_group_id = request.GET.get('new_group_id')


        if not group_id or not new_group_id:
            return Response({"error": "Both 'group_id' and 'new_group_id' are required."}, status=status.HTTP_400_BAD_REQUEST)

        ic(group_id, new_group_id, student_id)

        # Get the existing record
        instance = SecondaryStudentGroup.objects.filter(
            group__id=group_id,
            student__id=student_id
        ).first()

        if not instance:
            return Response({"error": "Secondary student group record not found."}, status=status.HTTP_404_NOT_FOUND)

        # Get the new secondary group
        new_group = get_object_or_404(SecondaryGroup, id=new_group_id)

        # Update and save
        instance.group = new_group
        instance.save()

        serializer = SecondaryStudentsGroupSerializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

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
        from django.db.models import Q

        students = StudentGroup.objects.filter(
            Q(group=group) & (Q(student__is_archived=False) | Q(lid__is_archived=False))
        ).count()

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
            created_at__gte=datetime.date.today(),
        ).distinct()

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
        return queryset.distinct()


    def get_paginated_response(self, data):
        return Response(data)


class GroupStudentDetail(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = StudentsGroupSerializer

    def get_queryset(self):
        id = self.kwargs.get('pk')
        print(id)

        qs = StudentGroup.objects.filter(Q(student=id) | Q(lid=id))

        user = self.request.GET.get("user")
        course = self.request.GET.get("course")

        if user:
            qs = qs.filter(student__user__id=user)
        if course:
            qs = qs.filter(group__course__id=course)

        return qs

class GroupStudentNoPgDetail(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = StudentsGroupSerializer
    pagination_class = None

    def get_queryset(self):
        id = self.kwargs.get('pk')
        print(id)

        return StudentGroup.objects.filter(Q(student=id) | Q(lid=id),)
    def get_paginated_response(self, data):
        return Response(data)


class SecondaryStudentList(ListCreateAPIView):
    serializer_class = SecondaryStudentsGroupSerializer
    queryset = SecondaryStudentGroup.objects.all()
    permission_classes = [IsAuthenticated]

    def get_queryset(self):

        qs = SecondaryStudentGroup.objects.all()

        search = self.request.GET.get("search")
        status = self.request.GET.get("status")
        group = self.request.GET.get("group")
        if group:
            qs = qs.filter(group__id=group)
        if search:
            student_search = Q(student__first_name__icontains=search) | Q(student__last_name__icontains=search)
            lid_search = Q(lid__first_name__icontains=search) | Q(lid__last_name__icontains=search)

            qs = qs.filter(student_search | lid_search)
        if status:
            qs = qs.filter(
                student__student_stage_type=status,
            )
        if self.request.user.role == 'ASSISTANT':
            qs = qs.filter(group__teacher__id=self.request.user.id)
        return qs


class SecondaryGroupList(ListAPIView):
    serializer_class = SecondaryGroupModelSerializer
    queryset = SecondaryGroup.objects.all()
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        status = self.request.query_params.get("status")
        id = self.kwargs.get('pk')

        queryset = SecondaryGroup.objects.all()

        if status:
            queryset = queryset.filter(student__status=status)
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
        start_date = self.request.query_params.get("start_date")
        end_date = self.request.query_params.get("end_date")

        # Base queryset - fix the filial filter
        base_queryset = StudentGroup.objects.filter(Q(student__is_archived=False) | Q(lid__is_archived=False))

        # Apply filial filter if provided
        if filial:
            # Check if filial is related through group
            base_queryset = base_queryset.filter(group__filial__id=filial)
            # OR if filial is directly on StudentGroup model:
            # base_queryset = base_queryset.filter(filial__id=filial)

        # Build specific querysets
        all_groups = base_queryset

        # Orders: groups with lids that are ordered and not students
        orders = base_queryset.filter(
            lid__isnull=False,
            lid__lid_stage_type="ORDERED_LID",
            lid__is_student=False
        )

        # Students: groups that have actual students
        students = base_queryset.filter(student__isnull=False)

        # Apply date filters
        if start_date and end_date:
            all_groups = all_groups.filter(created_at__gte=start_date, created_at__lte=end_date)
            orders = orders.filter(created_at__gte=start_date, created_at__lte=end_date)
            students = students.filter(created_at__gte=start_date, created_at__lte=end_date)
        elif start_date:  # Only start_date provided
            all_groups = all_groups.filter(created_at__gte=start_date)
            orders = orders.filter(created_at__gte=start_date)
            students = students.filter(created_at__gte=start_date)

        # Apply course filter
        if course:
            all_groups = all_groups.filter(group__course__id=course)
            orders = orders.filter(group__course__id=course)
            students = students.filter(group__course__id=course)

        # Apply teacher filter
        if teacher:
            all_groups = all_groups.filter(group__teacher__id=teacher)
            orders = orders.filter(group__teacher__id=teacher)
            students = students.filter(group__teacher__id=teacher)

        all_count = all_groups.count()
        students_count = students.count()
        orders_count = orders.count()

        print(f"Counts - All: {all_count}, Students: {students_count}, Orders: {orders_count}")

        return Response({
            "all": all_count,
            "students": students_count,
            "orders": orders_count,
        })


class SecondaryStudentCreate(ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = SecondaryStudentGroup.objects.all()
    serializer_class = SecondaryStudentsGroupSerializer

    pagination_class = None

    def get_queryset(self):
        id = self.request.query_params.get('group')
        filial = self.request.query_params.get("filial")
        search = self.request.query_params.get("search")

        queryset = SecondaryStudentGroup.objects.all()
        if id:
            queryset = queryset.filter(group__id=id)

        if filial:
            queryset = queryset.filter(filial__id=filial)

        return queryset

    def get_paginated_response(self, data):
        return Response(data)


class StudentGroupUpdate(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, **kwargs):
        group = request.data.get("group")
        student = request.data.get("student")
        add_group = request.data.get("add_group")

        if group and student and add_group:
            try:
                # Get the StudentGroup instance
                st = StudentGroup.objects.get(
                    student=student,
                    id=add_group,
                )

                # Get the new group object
                new_group = get_object_or_404(Group, id=group)

                # Update the group
                st.group = new_group
                st.save()

                return Response(
                    {"message": "Student group updated successfully"},
                    status=status.HTTP_200_OK
                )

            except StudentGroup.DoesNotExist:
                return Response(
                    {"error": "Student Group does not exist"},
                    status=status.HTTP_404_NOT_FOUND
                )
            except Group.DoesNotExist:
                return Response(
                    {"error": "Target group does not exist"},
                    status=status.HTTP_404_NOT_FOUND
                )

        else:
            return Response(
                {"error": "Missing required parameters: group, student, and add_group"},
                status=status.HTTP_400_BAD_REQUEST
            )

