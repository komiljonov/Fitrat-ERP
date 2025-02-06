from django.utils.module_loading import import_string
from rest_framework import serializers

from .models import Lesson, FirstLLesson
from ..attendance.models import Attendance
from ..course.models import Course
from ..groups.models import Group
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


class LessonScheduleSerializer(serializers.ModelSerializer):
    teacher_name = serializers.SerializerMethodField()
    room_number = serializers.SerializerMethodField()
    group_name = serializers.SerializerMethodField()
    scheduled_day_type = serializers.SerializerMethodField()
    started_at = serializers.SerializerMethodField()
    ended_at = serializers.SerializerMethodField()

    class Meta:
        model = Group
        fields = [
            'subject_name',
            'subject_label',
            'teacher_name',
            'room_number',
            'group_name',
            'scheduled_day_type',
            'started_at',
            'ended_at'
        ]

    def get_subject_name(self, obj):
        subject = Group.objects.get(id=obj.id).course.subject.name
        return subject

    def get_subject_label(self, obj):
        subject = Group.objects.get(id=obj.id).course.subject.label
        return subject

    def get_teacher_name(self, obj):
        teacher = obj.teacher
        return teacher.full_name if teacher else None

    def get_room_number(self, obj):
        room = Group.objects.get(id=obj.id).room_number.room_number
        return room

    def get_group_name(self, obj):
        return obj.name

    def get_scheduled_day_type(self, obj):
        return [day.name for day in obj.scheduled_day_type.all()]

    def get_started_at(self, obj):
        return obj.started_at.strftime('%H:%M')

    def get_ended_at(self, obj):
        return obj.ended_at.strftime('%H:%M')


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
