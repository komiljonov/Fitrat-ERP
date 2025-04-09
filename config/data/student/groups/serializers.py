from datetime import date

from django.db.models import Count
from rest_framework import serializers

from .lesson_date_calculator import calculate_lessons
from .models import Group, Day, Room, SecondaryGroup
from .room_filings_calculate import calculate_room_filling_statistics
from ..attendance.models import Attendance
from ..course.models import Course
from ..course.serializers import CourseSerializer
from ..studentgroup.models import StudentGroup, SecondaryStudentGroup
from ..subject.models import Theme, Level
from ...account.models import CustomUser
from ...account.serializers import UserSerializer


class DaySerializer(serializers.ModelSerializer):
    class Meta:
        model = Day
        fields = ["id", "name", ]


class GroupSerializer(serializers.ModelSerializer):
    teacher = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())
    scheduled_day_type = serializers.PrimaryKeyRelatedField(queryset=Day.objects.all(), many=True)
    student_count = serializers.SerializerMethodField()
    lessons_count = serializers.SerializerMethodField()
    current_theme = serializers.SerializerMethodField()
    room_number = serializers.PrimaryKeyRelatedField(queryset=Room.objects.all(), allow_null=True)
    course = serializers.PrimaryKeyRelatedField(queryset=Course.objects.all(), allow_null=True)
    subject = serializers.SerializerMethodField()
    level = serializers.SerializerMethodField()

    class Meta:
        model = Group
        fields = [
            'id',
            'name',
            'teacher',
            'secondary_teacher',
            'status',
            'course',
            'subject',
            "level",
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
            'current_theme',
            "created_at",
        ]

    def get_subject(self, obj):
        return Group.objects.filter(pk=obj.pk).values("course__subject", "course__subject__name").first()

    def get_level(self, obj):
        level = Level.objects.filter(courses=obj.course).first()
        if level:
            return {"id": level.id, "name": level.name}  # return only what's needed
        return None

    def get_current_theme(self, obj):
        today = date.today()

        # Ensures we compare only the date and remove duplicate themes
        attendance = (
            Attendance.objects.filter(group=obj, created_at__date=today)
            .values("theme", "repeated")
            .distinct()  # Remove duplicates
        )

        return list(attendance)

    def get_lessons_count(self, obj):
        total_lessons = Theme.objects.filter(course__group=obj).count()

        attended_lessons = (
            Attendance.objects.filter(theme__course__group=obj)
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
        rep["room_number"] = RoomsSerializer(instance.room_number).data
        rep["course"] = CourseSerializer(instance.course).data
        return rep

    def create(self, validated_data):
        scheduled_day_type_data = validated_data.pop('scheduled_day_type', [])
        filial = validated_data.pop("filial", None)
        if not filial:
            request = self.context.get("request")  #
            if request and hasattr(request.user, "filial"):
                filial = request.user.filial.first()

        if not filial:
            raise serializers.ValidationError({"filial": "Filial could not be determined."})

        group = Group.objects.create(filial=filial, **validated_data)

        group.scheduled_day_type.set(scheduled_day_type_data)

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
            lesson_dates = calculate_lessons(start_date, end_date, ','.join(lesson_days), holidays, days_off, )
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

    def create(self, validated_data):
        filial = validated_data.pop("filial", None)
        if not filial:
            request = self.context.get("request")  #
            if request and hasattr(request.user, "filial"):
                filial = request.user.filial.first()

        if not filial:
            raise serializers.ValidationError({"filial": "Filial could not be determined."})

        room = Room.objects.create(filial=filial, **validated_data)
        return room


class RoomFilterSerializer(serializers.ModelSerializer):
    lessons_start_time = serializers.CharField()
    lessons_end_time = serializers.CharField()
    average_lesson_hours = serializers.CharField()

    class Meta:
        model = Room
        fields = [
            'id',
            'room_number',
            'room_filling',
            'created_at',
            'updated_at',
            'lessons_start_time',  # Include here
            'lessons_end_time',  # Include here
            'average_lesson_hours'  # Include here
        ]

    def calculate(self, validated_data):
        lessons_start_time = validated_data.pop("lessons_start_time", None)
        lessons_end_time = validated_data.pop("lessons_end_time", None)
        average_lesson_hours = validated_data.pop("average_lesson_hours", 2)

        lessons_start_time = lessons_start_time.strftime("%H:%M") if lessons_start_time else "08:00"
        lessons_end_time = lessons_end_time.strftime("%H:%M") if lessons_end_time else "20:00"

        average_students_filling = calculate_room_filling_statistics(
            room_id=validated_data.get("id"),
            lessons_start_time=lessons_start_time,
            lessons_end_time=lessons_end_time,
            lesson_duration=average_lesson_hours,
        )

        return average_students_filling


class SecondaryGroupSerializer(serializers.ModelSerializer):
    group = serializers.PrimaryKeyRelatedField(queryset=Group.objects.all())
    teacher = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())
    student_count = serializers.SerializerMethodField()

    class Meta:
        model = SecondaryGroup
        fields = [
            'id',
            'name',
            'group',
            'teacher',
            'scheduled_day_type',  # This is a ManyToManyField
            'status',
            'student_count',
            'started_at',
            'ended_at',
            'start_date',
            'finish_date',
            'created_at',
            'updated_at',
        ]

    def get_student_count(self, obj):
        return SecondaryStudentGroup.objects.filter(group=obj).count()

    def create(self, validated_data):
        """
        Handles M2M relation (scheduled_day_type) separately using set().
        """
        scheduled_day_types = validated_data.pop("scheduled_day_type", [])  # Extract M2M field
        filial = validated_data.pop("filial", None)

        # Determine filial from request if not provided
        if not filial:
            request = self.context.get("request")
            if request and hasattr(request.user, "filial"):
                filial = request.user.filial.first()

        if not filial:
            raise serializers.ValidationError({"filial": "Filial could not be determined."})

        # Create the SecondaryGroup instance without M2M
        group = SecondaryGroup.objects.create(filial=filial, **validated_data)

        # Set the ManyToMany field properly
        if scheduled_day_types:
            group.scheduled_day_type.set(scheduled_day_types)  # Correct M2M assignment

        return group

    def update(self, instance, validated_data):
        """
        Handles M2M relation (scheduled_day_type) separately during update.
        """
        scheduled_day_types = validated_data.pop("scheduled_day_type", None)  # Extract M2M field

        # Update other fields normally
        instance = super().update(instance, validated_data)

        # Update ManyToMany relation only if provided
        if scheduled_day_types is not None:
            instance.scheduled_day_type.set(scheduled_day_types)  # Correct M2M update

        return instance

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['teacher'] = UserSerializer(instance.teacher).data
        rep['group'] = GroupSerializer(instance.group).data
        return rep


class SecondarygroupModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = SecondaryGroup
        fields = ['id', 'name']
