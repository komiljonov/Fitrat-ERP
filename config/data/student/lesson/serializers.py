import datetime

from django.utils.module_loading import import_string
from rest_framework import serializers

from .models import Lesson, FirstLLesson
from ..attendance.models import Attendance
from ..course.models import Course
from ..groups.lesson_date_calculator import calculate_lessons
from ..groups.models import Group, Room
from ..groups.serializers import GroupSerializer
from ..subject.models import Subject
from ...lid.new_lid.models import Lid


class LessonSerializer(serializers.ModelSerializer):
    group = serializers.PrimaryKeyRelatedField(queryset=Group.objects.all())
    attendance = serializers.SerializerMethodField()

    teacher = serializers.StringRelatedField(source="group.teacher")
    room = serializers.StringRelatedField(source="group.room_number")

    # current_theme = serializers.SerializerMethodField()

    class Meta:
        model = Lesson
        fields = [
            "id",
            'name',
            "subject",
            'type',
            'group',
            'comment',
            'teacher',
            'room',
            'theme',
            # 'current_theme',
            'lesson_status',
            'lessons_count',
            'attendance',
            'created_at',
            'updated_at',
        ]

    # def get_current_theme(self, obj):
    #     """
    #     Calculate lesson dates based on the group data.
    #     """
    #     # Retrieve required data from the Group instance
    #     start_date = obj.start_date.strftime("%Y-%m-%d") if obj.start_date else None
    #     end_date = obj.finish_date.strftime("%Y-%m-%d") if obj.finish_date else None
    #     lesson_type = obj.scheduled_day_type  # Assume this corresponds to 'ODD', 'EVEN', or 'EVERYDAY'
    #     holidays = ['']  # Replace with actual logic to fetch holidays, e.g., from another model
    #     days_off = ["Sunday"]  # Replace or fetch from settings/config
    #
    #     if start_date and end_date:
    #         # Use the calculate_lessons function to get lesson dates
    #         lesson_dates = calculate_lessons(start_date, end_date, lesson_type, holidays, days_off)
    #         return lesson_dates
    #     return []

    def get_attendance(self, obj):
        attendance = Attendance.objects.filter(lesson=obj)
        AttendanceSerializer = import_string('data.student.attendance.serializers.AttendanceSerializer')
        return AttendanceSerializer(attendance, many=True).data

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['group'] = GroupSerializer(instance.group).data
        return rep



# class LessonScheduleSerializer(serializers.ModelSerializer):
#     subject = serializers.SerializerMethodField()
#     room = serializers.SerializerMethodField()
#     subject_label = serializers.SerializerMethodField()
#     teacher_name = serializers.SerializerMethodField()
#     started_at = serializers.SerializerMethodField()
#     ended_at = serializers.SerializerMethodField()
#     scheduled_day_type = serializers.SerializerMethodField()
#     days = serializers.SerializerMethodField()  # Include 'days' for today's and other days schedules
#
#     class Meta:
#         model = Group
#         fields = [
#             'subject',
#             'subject_label',
#             'teacher_name',
#             'room',
#             'name',
#             'scheduled_day_type',
#             'started_at',
#             'ended_at',
#             'days',  # Add 'days' to return the schedule dates
#         ]
#
#     def get_subject(self, obj):
#         return obj.course.subject.name if obj.course and obj.course.subject else None
#
#     def get_room(self, obj):
#         room = Group.objects.filter(id=obj.id).values_list('room_number', flat=True).first()
#         if room:
#             room_obj = Room.objects.filter(id=room).first()
#             return room_obj.room_number if room_obj else None
#
#     def get_subject_label(self, obj):
#         return obj.course.subject.label if obj.course and obj.course.subject else None
#
#     def get_teacher_name(self, obj):
#         fullname = f"{obj.teacher.first_name if obj.teacher.first_name else ''} {obj.teacher.last_name if obj.teacher.last_name else ''}"
#         return fullname if obj.teacher else None
#
#     def get_scheduled_day_type(self, obj):
#         return [day.name for day in obj.scheduled_day_type.all()] if obj.scheduled_day_type else []
#
#     def get_started_at(self, obj):
#         return obj.started_at.strftime('%H:%M') if obj.started_at else None
#
#     def get_ended_at(self, obj):
#         return obj.ended_at.strftime('%H:%M') if obj.ended_at else None
#
#     from datetime import datetime

import datetime
from datetime import timedelta

class LessonScheduleSerializer(serializers.ModelSerializer):
    subject = serializers.SerializerMethodField()
    room = serializers.SerializerMethodField()
    subject_label = serializers.SerializerMethodField()
    teacher_name = serializers.SerializerMethodField()
    started_at = serializers.SerializerMethodField()
    ended_at = serializers.SerializerMethodField()
    scheduled_day_type = serializers.SerializerMethodField()
    days = serializers.SerializerMethodField()  # Add the days field

    class Meta:
        model = Group
        fields = [
            'subject',
            'subject_label',
            'teacher_name',
            'room',
            'name',
            'scheduled_day_type',
            'started_at',
            'ended_at',
            'days',
        ]

    def get_subject(self, obj):
        return obj.course.subject.name if obj.course and obj.course.subject else None

    def get_room(self, obj):
        room = Group.objects.filter(id=obj.id).values_list('room_number', flat=True).first()
        if room:
            room_obj = Room.objects.filter(id=room).first()
            return room_obj.room_number if room_obj else None

    def get_subject_label(self, obj):
        return obj.course.subject.label if obj.course and obj.course.subject else None

    def get_teacher_name(self, obj):
        fullname = f"{obj.teacher.first_name if obj.teacher.first_name else ''} {obj.teacher.last_name if obj.teacher else ''}"
        return fullname if obj.teacher else None

    def get_scheduled_day_type(self, obj):
        return [day.name for day in obj.scheduled_day_type.all()] if obj.scheduled_day_type else []

    def get_started_at(self, obj):
        return obj.started_at.strftime('%H:%M') if obj.started_at else None

    def get_ended_at(self, obj):
        return obj.ended_at.strftime('%H:%M') if obj.ended_at else None

    def get_days(self, obj):
        today = datetime.datetime.today().date()
        upcoming_days = []
        schedule_days = obj.scheduled_day_type.all()  # Assuming scheduled_day_type contains day objects

        # Get the list of weekdays in string format
        weekdays = {
            "Monday": 0,
            "Tuesday": 1,
            "Wednesday": 2,
            "Thursday": 3,
            "Friday": 4,
            "Saturday": 5,
            "Sunday": 6
        }

        # Loop through each scheduled day and calculate the next occurrence
        for day in schedule_days:
            scheduled_day = day.name

            if scheduled_day in weekdays:
                day_num = weekdays[scheduled_day]
                next_occurrence = self.get_next_day_of_week(today, day_num)

                if next_occurrence:
                    if next_occurrence == today:
                        upcoming_days.append(f"Today ({today})")
                    elif next_occurrence > today:
                        upcoming_days.append(f"Upcoming ({next_occurrence})")

        # Sort the upcoming days from today and within the next month
        upcoming_days.sort(key=lambda x: datetime.datetime.strptime(x.split('(')[1][:-1], "%Y-%m-%d"))

        # Limit results to the next month
        next_month = today + timedelta(days=30)
        upcoming_days = [day for day in upcoming_days if datetime.datetime.strptime(day.split('(')[1][:-1], "%Y-%m-%d").date() <= next_month]

        return upcoming_days if upcoming_days else ["No upcoming lessons"]

    def get_next_day_of_week(self, current_date, target_day_num):
        """
        Returns the next occurrence of a target weekday after the current date.
        current_date: datetime.date object (today's date)
        target_day_num: int (weekday number, 0 for Monday, 6 for Sunday)
        """
        days_ahead = target_day_num - current_date.weekday()

        if days_ahead <= 0:
            days_ahead += 7  # If the target day is earlier in the week, schedule it for next week

        next_occurrence = current_date + timedelta(days=days_ahead)
        return next_occurrence



class FirstLessonSerializer(serializers.ModelSerializer):
    lid = serializers.PrimaryKeyRelatedField(queryset=Lid.objects.all(), allow_null=True)
    class Meta:
        model = FirstLLesson
        fields = [
            'id',
            'lid',
            'group',
            'date',
            'time',
            'comment',
            'creator',
        ]

    def update(self, instance, validated_data):
        # Check if 'creator' is present and set it to the current user
        creator = validated_data.pop('creator', None)
        if creator is not None:
            instance.creator = self.context['request'].user

        # Proceed with the standard update logic
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['group'] = GroupSerializer(instance.group).data
        return rep
