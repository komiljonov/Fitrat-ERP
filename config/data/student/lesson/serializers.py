from datetime import date, timedelta

from django.utils.module_loading import import_string
from rest_framework import serializers

from .models import Lesson, FirstLLesson
from ..attendance.models import Attendance
from ..groups.lesson_date_calculator import calculate_lessons
from ..groups.models import Group
from ..groups.serializers import GroupSerializer
from ..student.models import Student
from ..student.serializers import StudentSerializer
from ..studentgroup.models import StudentGroup
from ..studentgroup.serializers import StudentsGroupSerializer
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
    group_id = serializers.UUIDField(write_only=True)
    subject_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = Lesson
        fields = [
            'id', 'name', 'group_id', 'subject_id',
            'day', 'start_time', 'end_time', 'comment', 'lesson_status', 'lessons_count'
        ]
        read_only_fields = ['id', 'lesson_status', 'lessons_count']

    def validate(self, data):
        group_id = data.get('group_id')
        group = Group.objects.get(id=group_id)
        room_number = group.room_number
        day = data.get('day')
        start_time = data.get('start_time')
        end_time = data.get('end_time')

        # Check if group exists
        try:
            group = Group.objects.get(id=group_id)
        except Group.DoesNotExist:
            raise serializers.ValidationError({"group_id": "Group not found."})
        data['group'] = group  # Attach group object for later use

        # Check for scheduling conflicts
        if Lesson.objects.filter(
                room_number=room_number,
                day=day,
                start_time__lt=end_time,  # Overlap: Starts before another lesson ends
                end_time__gt=start_time  # Overlap: Ends after another lesson starts
        ).exists():
            raise serializers.ValidationError({"schedule": "Conflict detected with an existing lesson."})

        return data

    def create(self, validated_data):
        """
        Create the lesson after validation.
        """
        group = validated_data.pop('group')
        subject_id = validated_data.pop('subject_id')

        # Create the lesson
        lesson = Lesson.objects.create(
            group=group,
            subject_id=subject_id,
            **validated_data
        )
        return lesson


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
