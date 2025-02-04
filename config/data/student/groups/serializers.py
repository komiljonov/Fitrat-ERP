from django.db.models import Count
from rest_framework import serializers

from .lesson_date_calculator import calculate_lessons
from .models import Group, Day, Room, SecondaryGroup
from ..attendance.models import Attendance
from ..lesson.models import Lesson
from ..studentgroup.models import StudentGroup
from ..subject.models import Theme
from ...account.models import CustomUser
from ...account.serializers import UserSerializer


class DaySerializer(serializers.ModelSerializer):
    class Meta:
        model = Day
        fields = ["id","name",]


class GroupSerializer(serializers.ModelSerializer):
    teacher = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())
    scheduled_day_type = serializers.PrimaryKeyRelatedField(queryset=Day.objects.all(), many=True)
    student_count = serializers.SerializerMethodField()
    lessons_count = serializers.SerializerMethodField()

    class Meta:
        model = Group
        fields = [
            'id',
            'name',
            'teacher',
            'secondary_teacher',
            'status',
            'course',
            'student_count',
            'lessons_count',
            'room_number',
            'price_type',
            'price',
            'scheduled_day_type',
            'comment',
            'started_at',
            'ended_at',
            'start_date',
            'finish_date',
            'is_secondary',
        ]

    def get_lessons_count(self, obj):
        total_lessons = Theme.objects.filter(group=obj).count()

        attended_lessons = (
            Attendance.objects.filter(theme__group=obj)
            .values("theme")  # Group by lesson
            .annotate(attended_count=Count("id"))  # Count attendance per lesson
            .count()  # Count unique lessons with attendance records
        )

        return {
            "lessons": total_lessons,  # Total lessons in the group
            "attended": attended_lessons,  # Lessons that have attendance records
        }

    def get_student_count(self, obj):
        student_count = StudentGroup.objects.filter(group=obj).count()
        return student_count

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['teacher'] = UserSerializer(instance.teacher).data
        return rep

    def create(self, validated_data):
        scheduled_day_type_data = validated_data.pop('scheduled_day_type', [])
        group = Group.objects.create(**validated_data)

        # `scheduled_day_type` is already a list of Day instances due to PrimaryKeyRelatedField
        group.scheduled_day_type.set(scheduled_day_type_data)  # Using `.set()` to update the Many-to-Many field

        return group


class GroupLessonSerializer(serializers.ModelSerializer):
    group_lesson_dates = serializers.SerializerMethodField()  # Add this field

    class Meta:
        model = Group
        fields = [
            'id',
            'name',
            'teacher',
            'status',
            'room_number',
            'price_type',
            'course',
            'price',
            'scheduled_day_type',
            'comment',
            'started_at',
            'ended_at',

            'start_date',
            'finish_date',
            'group_lesson_dates',  # Include the new field
        ]

    def get_group_lesson_dates(self, obj):
        """
        Calculate lesson dates based on the group data.
        """
        # Retrieve required data from the Group instance
        start_date = obj.start_date.strftime("%Y-%m-%d") if obj.start_date else None
        end_date = obj.finish_date.strftime("%Y-%m-%d") if obj.finish_date else None

        # If the lesson type is a Many-to-Many field, get the weekday names
        lesson_days_queryset = obj.scheduled_day_type.all()  # This retrieves the related days
        lesson_days = [day.name for day in
                       lesson_days_queryset]  # Assuming 'name' stores the weekday name (e.g., 'Monday')

        holidays = ['']  # Replace with actual logic to fetch holidays, e.g., from another model
        days_off = ["Yakshanba"]  # Replace or fetch from settings/config

        if start_date and end_date:
            # Use the calculate_lessons function to get lesson dates
            lesson_dates = calculate_lessons(start_date, end_date, ','.join(lesson_days), holidays, days_off,)
            return lesson_dates
        return []


class RoomsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = [
            'id',
            'room_number',
            'room_filling',
            'created_at',
            'updated_at',
        ]


class SecondaryGroupSerializer(serializers.ModelSerializer):
    group = serializers.PrimaryKeyRelatedField(queryset=Group.objects.all())
    teacher = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())
    class Meta:
        model = SecondaryGroup
        fields = [
            'id',
            'name',
            'group',
            'teacher',
            'scheduled_day_type',
            'status',

            'started_at',
            'ended_at',

            'start_date',
            'finish_date',

            'created_at',
            'updated_at',
        ]
    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['teacher'] = UserSerializer(instance.teacher).data
        rep['group'] = GroupSerializer(instance.group).data
        return rep
