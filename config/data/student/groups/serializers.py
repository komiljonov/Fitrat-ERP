from rest_framework import serializers

from .lesson_date_calculator import calculate_lessons
from .models import Group, Subject, Level
from ..subject.serializers import SubjectSerializer, LevelSerializer
from ...account.models import CustomUser
from ...account.serializers import UserSerializer


class GroupSerializer(serializers.ModelSerializer):
    teacher = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())
    subject = serializers.PrimaryKeyRelatedField(queryset=Subject.objects.all())
    level = serializers.PrimaryKeyRelatedField(queryset=Level.objects.all())

    class Meta:
        model = Group
        fields = [
            'id',
            'name',
            'subject',
            'level',
            'teacher',
            'status',
            'room_number',
            'price_type',
            'price',
            'scheduled_day_type',
            'group_type',
            'comment',
            'started_at',
            'ended_at',
            'start_date',
            'finish_date',
        ]

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['teacher'] = UserSerializer(instance.teacher).data
        rep['subject'] = SubjectSerializer(instance.subject).data
        rep['level'] = LevelSerializer(instance.level).data
        return rep


class GroupLessonSerializer(serializers.ModelSerializer):
    group_lesson_dates = serializers.SerializerMethodField()  # Add this field

    class Meta:
        model = Group
        fields = [
            'id',
            'name',
            'subject',
            'level',
            'teacher',
            'status',
            'room_number',
            'price_type',
            'price',
            'scheduled_day_type',
            'group_type',
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
        lesson_type = obj.scheduled_day_type  # Assume this corresponds to 'ODD', 'EVEN', or 'EVERYDAY'
        holidays = ['']  # Replace with actual logic to fetch holidays, e.g., from another model
        days_off = ["Sunday"]  # Replace or fetch from settings/config

        if start_date and end_date:
            # Use the calculate_lessons function to get lesson dates
            lesson_dates = calculate_lessons(start_date, end_date, lesson_type, holidays, days_off)
            return lesson_dates
        return []
