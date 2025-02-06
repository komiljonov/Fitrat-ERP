from django.utils.module_loading import import_string
from rest_framework import serializers

from .models import Lesson, FirstLLesson
from ..attendance.models import Attendance
from ..course.models import Course
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


from rest_framework import serializers
from .models import Group

class LessonScheduleSerializer(serializers.ModelSerializer):
    subject = serializers.SerializerMethodField()
    room = serializers.SerializerMethodField()
    subject_label = serializers.SerializerMethodField()
    teacher_name = serializers.SerializerMethodField()
    started_at = serializers.SerializerMethodField()
    ended_at = serializers.SerializerMethodField()
    scheduled_day_type = serializers.SerializerMethodField()

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
            'ended_at'
        ]

    def get_subject(self, obj):
        return obj.course.subject.name if obj.course and obj.course.subject else None

    def get_room(self, obj):
        room = Group.objects.filter(id=obj.id).values_list('room_number',
                                                           flat=True).first()  # Use first() for efficiency
        if room:
            room_obj = Room.objects.filter(id=room).first()  # Fetch the actual Room object
            return room_obj.room_number if room_obj else None  # Return a serializable field, like room_number

    def get_subject_label(self, obj):
        return obj.course.subject.label if obj.course and obj.course.subject else None

    def get_teacher_name(self, obj):
        fullname = f"{obj.teacher.first_name if obj.teacher.first_name else ""}  {obj.teacher.last_name if obj.teacher and obj.teacher.first_name else ""}"
        return fullname if obj.teacher else None

    def get_scheduled_day_type(self, obj):
        return [day.name for day in obj.scheduled_day_type.all()] if obj.scheduled_day_type else []

    def get_started_at(self, obj):
        return obj.started_at.strftime('%H:%M') if obj.started_at else None

    def get_ended_at(self, obj):
        return obj.ended_at.strftime('%H:%M') if obj.ended_at else None



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
