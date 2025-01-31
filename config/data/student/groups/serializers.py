from rest_framework import serializers
from rest_framework.generics import ListCreateAPIView

from .lesson_date_calculator import calculate_lessons
from .models import Group, Subject, Level, Day, Room, SecondaryGroup
from ..studentgroup.models import StudentGroup
from ..subject.serializers import SubjectSerializer, LevelSerializer
from ...account.models import CustomUser
from ...account.serializers import UserSerializer


class DaySerializer(serializers.ModelSerializer):
    class Meta:
        model = Day
        fields = ["id","name",]



class GroupSerializer(serializers.ModelSerializer):
    teacher = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())
    scheduled_day_type = serializers.PrimaryKeyRelatedField(queryset=Day.objects.all(),
                                                            many=True)
    student_count = serializers.SerializerMethodField()
    class Meta:
        model = Group
        fields = [
            'id',
            'name',
            'teacher',
            'status',
            'course',
            'student_count',
            'room_number',
            'price_type',
            'price',
            'scheduled_day_type',
            'comment',
            'started_at',
            'ended_at',
            'start_date',
            'finish_date',
        ]

    def get_student_count(self,obj):
        student_count = StudentGroup.objects.filter(group=obj).count()
        return student_count

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['teacher'] = UserSerializer(instance.teacher).data

        return rep

    def create(self, validated_data):
        scheduled_day_data = validated_data.pop('scheduled_day_type', [])
        group = Group.objects.create(**validated_data)  # Create the Group object

        # Associate the days (scheduled_day_type) to the group
        for day_id in scheduled_day_data:
            day = Day.objects.get(id=day_id)  # Get the Day object using its ID
            group.scheduled_day_type.add(day)  # Add the day to the group

        return group

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
        lesson_type = obj.scheduled_day_type  # Assume this corresponds to 'ODD', 'EVEN', or 'EVERYDAY'
        holidays = ['']  # Replace with actual logic to fetch holidays, e.g., from another model
        days_off = ["Sunday"]  # Replace or fetch from settings/config

        if start_date and end_date:
            # Use the calculate_lessons function to get lesson dates
            lesson_dates = calculate_lessons(start_date, end_date, lesson_type, holidays, days_off)
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
