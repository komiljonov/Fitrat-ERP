from datetime import datetime

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.generics import ListAPIView, ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from .models import Group, Room, SecondaryGroup, Day
from .serializers import GroupSerializer, GroupLessonSerializer, RoomsSerializer, SecondaryGroupSerializer, \
    DaySerializer
from ..lesson.models import ExtraLesson, ExtraLessonGroup
from ..lesson.serializers import LessonScheduleSerializer, LessonScheduleWebSerializer
from ..lesson.views import LessonSchedule


class StudentGroupsView(ListCreateAPIView):
    queryset = Group.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = GroupSerializer
    filter_backends = (DjangoFilterBackend, OrderingFilter, SearchFilter)

    search_fields = ('name', 'scheduled_day_type__name', "status",'teacher__id',
                     'course__subject__id','course__level__id')
    ordering_fields = ('name', 'scheduled_day_type', 'start_date',
                       'end_date', 'price_type', "status",'teacher__id',
                     'course__subject__id','course__level__id')
    filterset_fields = ('name', 'scheduled_day_type__name',
                        'price_type', "status",'teacher__id',
                     'course__subject__id','course__level__id')


class StudentRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Group.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = GroupSerializer


class StudentListAPIView(ListAPIView):
    queryset = Group.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = GroupSerializer

    def get_queryset(self):
        filter = {}
        queryset = Group.objects.all()
        course = self.request.query_params.get('course', None)
        teacher = self.request.query_params.get('teacher', None)
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)
        if course:
            filter['course__id'] = course
        if teacher:
            filter['teacher__id'] = teacher
        if start_date:
            filter['created_at__gte'] = start_date
        if end_date:
            filter['created_at__lte'] = end_date
        return queryset.filter(**filter)
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


class TeachersGroupsView(ListAPIView):
    queryset = Group.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = GroupSerializer

    def get_queryset(self):
        teacher_id = self.kwargs.get('pk')
        if teacher_id:
            teacher_groups = Group.objects.filter(teacher__id=teacher_id)
            return teacher_groups
        return Group.objects.none()


class RoomListAPIView(ListCreateAPIView):
    queryset = Room.objects.all()
    serializer_class = RoomsSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = (DjangoFilterBackend, OrderingFilter, SearchFilter)
    search_fields = ('room_number', 'room_filling')
    ordering_fields = ('room_number', 'room_filling')
    filterset_fields = ('room_number', 'room_filling')

    def get_queryset(self):
        filial = self.request.query_params.get('filial', None)
        if filial:
            return Room.objects.filter(filial=filial)
        return Room.objects.all()  # Ensure it always returns a queryset

    def perform_create(self, serializer):
        """Automatically assign the requesting user's filial when creating a room."""
        serializer.save(filial=self.request.user.filial.first())


class RoomFilterView(ListAPIView):
    queryset = Room.objects.all()
    serializer_class = RoomsSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = (DjangoFilterBackend, OrderingFilter, SearchFilter)
    search_fields = ('room_number', 'room_filling')
    ordering_fields = ('room_number', 'room_filling')
    filterset_fields = ('room_number', 'room_filling')





class RoomRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Room.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = RoomsSerializer


class RoomNoPG(ListAPIView):
    queryset = Room.objects.all()
    serializer_class = RoomsSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = (DjangoFilterBackend, OrderingFilter, SearchFilter)
    search_fields = ('room_number', 'room_filling')
    ordering_fields = ('room_number', 'room_filling')
    filterset_fields = ('room_number', 'room_filling')

    def get_paginated_response(self, data):
        return Response(data)


class SecondaryGroupsView(ListCreateAPIView):
    queryset = SecondaryGroup.objects.all()
    serializer_class = SecondaryGroupSerializer
    permission_classes = [IsAuthenticated]

    filter_backends = (DjangoFilterBackend, OrderingFilter, SearchFilter)
    search_fields = ('name', 'scheduled_day_type__name')
    ordering_fields = ('name', 'scheduled_day_type', 'start_date', 'end_date',)
    filterset_fields = ('name', 'scheduled_day_type',)


class SecondaryGroupRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    queryset = SecondaryGroup.objects.all()
    serializer_class = SecondaryGroupSerializer
    permission_classes = [IsAuthenticated]


class SecondaryNoPG(ListAPIView):
    queryset = SecondaryGroup.objects.all()
    serializer_class = SecondaryGroupSerializer

    def get_paginated_response(self, data):
        return Response(data)


class DaysAPIView(ListCreateAPIView):
    queryset = Day.objects.all()
    serializer_class = DaySerializer
    permission_classes = [IsAuthenticated]


class DaysNoPG(ListAPIView):
    queryset = Day.objects.all()
    serializer_class = DaySerializer
    permission_classes = [IsAuthenticated]

    def get_paginated_response(self, data):
        return Response(data)




class GroupSchedule(ListAPIView):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Group.objects.all()
        start_date = self.request.query_params.get('from',None)
        end_date = self.request.query_params.get('to', None)

        filial = self.request.user.filial
        room_id = self.request.query_params.get('room')
        if room_id:
            return (queryset.filter(
                room_number=room_id,
                room_number__filial=filial,
            ).order_by('started_at'))

        if start_date and end_date:
            return (queryset.filter(
                room_number=room_id,
                room_number__filial=filial,
                created_at__gte=start_date,
                created_at__lte=end_date,
            ).order_by('started_at'))
        return queryset


from collections import defaultdict
import datetime
from rest_framework.response import Response
from rest_framework.generics import ListAPIView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter


class LessonScheduleListApi(ListAPIView):
    serializer_class = LessonScheduleSerializer
    queryset = Group.objects.filter(status="ACTIVE")
    filter_backends = (DjangoFilterBackend, OrderingFilter, SearchFilter)

    ordering_fields = ['start_date', 'end_date', 'name']
    search_fields = ['name', 'teacher__id', 'course__subject__name', 'room_number']
    filterset_fields = ('name', 'teacher__id', 'course__subject__name', 'room_number')

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)

        # Get the date filter from query params (optional)
        date_filter = self.request.query_params.get('date', None)
        date_filter = datetime.datetime.strptime(date_filter, "%d-%m-%Y").date() if date_filter else None

        # Prepare to collect lessons grouped by date
        lessons_by_date = defaultdict(list)

        # Collect lessons from the main schedule
        for item in serializer.data:
            days = item.get('days', [])
            for day in days:
                lesson_date = datetime.datetime.strptime(day['date'], "%d-%m-%Y").date()
                if date_filter and lesson_date != date_filter:
                    continue
                lessons_by_date[lesson_date].extend(day['lessons'])

        # Fetch extra lessons for the groups (ExtraLessonGroup)
        extra_lessons_group = ExtraLessonGroup.objects.filter(
            group__in=queryset,
            created_at__gte=datetime.date.today(),
        )

        # Process extra lessons for groups
        for extra in extra_lessons_group:
            lesson_date = extra.date
            if date_filter and lesson_date != date_filter:
                continue
            lesson_data = {
                "subject": extra.group.course.subject.name if extra.group.course and extra.group.course.subject else None,
                "subject_label": extra.group.course.subject.label if extra.group.course and extra.group.course.subject else None,
                "teacher_name": f"{extra.group.teacher.first_name if extra.group.teacher.first_name else ''} {extra.group.teacher.last_name if extra.group.teacher else ''}",
                "room": extra.group.room_number.room_number if extra.group.room_number else None,
                "name": extra.group.name,
                "status": "Extra_lessons",
                "started_at": extra.started_at.strftime('%H:%M') if extra.started_at else None,
                "ended_at": extra.ended_at.strftime('%H:%M') if extra.ended_at else None,
            }
            lessons_by_date[lesson_date].append(lesson_data)

        # Fetch extra lessons for individual students (ExtraLesson)
        extra_lessons_individual = ExtraLesson.objects.filter(
            date__gte=datetime.date.today(),
        )

        # Process extra lessons for individual students
        for extra in extra_lessons_individual:
            lesson_date = extra.date
            if date_filter and lesson_date != date_filter:
                continue
            lesson_data = {
                "name": f"{extra.student.first_name} {extra.student.last_name}" if extra.student else None,  # You can change this to any student info you need
                "comment": extra.comment,
                "teacher_name" : f"{extra.teacher.first_name} {extra.teacher.last_name}" if extra.teacher else None,
                "status": "Extra_lessons",
                "room": extra.room.room_number if extra.room else None,
                "started_at": extra.started_at.strftime('%H:%M') if extra.started_at else None,
                "ended_at": extra.ended_at.strftime('%H:%M') if extra.ended_at else None,
                "is_payable": extra.is_payable,
                "is_attendance": extra.is_attendance,
            }
            lessons_by_date[lesson_date].append(lesson_data)

        # Sort the dates in ascending order
        sorted_dates = sorted(lessons_by_date.keys())

        # Prepare the sorted response
        sorted_lessons = []
        for lesson_date in sorted_dates:
            sorted_lessons.append({
                "date": lesson_date.strftime('%d-%m-%Y'),
                "lessons": lessons_by_date[lesson_date]
            })

        return Response(sorted_lessons)



class LessonScheduleWebListApi(ListAPIView):
    serializer_class = LessonScheduleWebSerializer
    queryset = Group.objects.filter(status="ACTIVE")
    filter_backends = (DjangoFilterBackend, OrderingFilter, SearchFilter)

    ordering_fields = ['start_date', 'end_date', 'name']
    search_fields = ['name', 'teacher__id', 'course__subject__name', 'room_number']
    filterset_fields = ('name', 'teacher__id', 'course__subject__name', 'room_number')

    def get_queryset(self):
        subject =self.request.query_params.get('subject')
        teacher = self.request.query_params.get('teacher')
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        if subject:
            queryset = self.queryset.filter(
                group__course__subject_id=subject,
            )
        if teacher:
            queryset = self.queryset.filter(
                group__teacher_id=teacher,
            )
        if start_date:
            queryset = self.queryset.filter(
                start_date=start_date
            )
        if start_date and end_date:
            queryset = self.queryset.filter(
                finish_date=end_date,
            )
        return queryset


    def get_paginated_response(self, data):
        return Response(data)
