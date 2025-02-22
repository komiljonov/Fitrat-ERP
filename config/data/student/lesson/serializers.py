import datetime

from django.utils.module_loading import import_string
from rest_framework import serializers

from .models import Lesson, FirstLLesson, ExtraLesson, ExtraLessonGroup
from ..attendance.models import Attendance
from ..groups.lesson_date_calculator import calculate_lessons
from ..groups.models import Group, Room
from ..groups.serializers import GroupSerializer, RoomsSerializer
from ..student.serializers import StudentSerializer
from ..studentgroup.models import StudentGroup
from ...account.serializers import UserSerializer
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


class LessonScheduleWebSerializer(serializers.ModelSerializer):
    subject = serializers.SerializerMethodField()
    room = serializers.SerializerMethodField()
    subject_label = serializers.SerializerMethodField()
    teacher_name = serializers.SerializerMethodField()
    started_at = serializers.SerializerMethodField()
    ended_at = serializers.SerializerMethodField()
    student_count = serializers.SerializerMethodField()
    room_fillings = serializers.SerializerMethodField()
    scheduled_day_type = serializers.SerializerMethodField()

    class Meta:
        model = Group
        fields = [
            'subject',
            'subject_label',
            'teacher_name',
            'room',
            'room_fillings',
            'student_count',
            'name',
            'scheduled_day_type',
            'started_at',
            'ended_at'
        ]

    def get_student_count(self, obj):
        return StudentGroup.objects.filter(group=obj).count()

    def get_room_fillings(self, obj):
        room = Group.objects.filter(id=obj.id).values_list('room_number', flat=True).first()
        if room:
            room_fillings = Room.objects.filter(id=room).first()
            return room_fillings.room_filling if room_fillings else None

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


class LessonScheduleSerializer(serializers.ModelSerializer):
    subject = serializers.SerializerMethodField()
    room = serializers.SerializerMethodField()
    subject_label = serializers.SerializerMethodField()
    teacher_name = serializers.SerializerMethodField()
    started_at = serializers.SerializerMethodField()
    ended_at = serializers.SerializerMethodField()
    scheduled_day_type = serializers.SerializerMethodField()
    days = serializers.SerializerMethodField()

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
        schedule_days = obj.scheduled_day_type.all()  # Assuming scheduled_day_type contains day objects
        lesson_schedule = {}

        start_date = datetime.datetime.today().strftime('%Y-%m-%d')
        end_date = datetime.datetime.today() + datetime.timedelta(days=30)

        lesson_type = ','.join([day.name for day in schedule_days])
        holidays = []
        days_off = ["Yakshanba"]

        # Get the scheduled lesson dates using the calculate_lessons function
        grouped_schedule = calculate_lessons(
            start_date=start_date,
            end_date=end_date.strftime('%Y-%m-%d'),
            lesson_type=lesson_type,
            holidays=holidays,
            days_off=days_off
        )

        # Collect lessons by date
        lesson_by_date = {}

        for month, lesson_dates in grouped_schedule.items():
            for lesson_date in lesson_dates:
                lesson_date_obj = datetime.datetime.strptime(lesson_date, "%Y-%m-%d").date()
                if lesson_date_obj >= today:
                    if lesson_date_obj not in lesson_by_date:
                        lesson_by_date[lesson_date_obj] = []

                    lesson_by_date[lesson_date_obj].append({
                        "subject": obj.course.subject.name if obj.course and obj.course.subject else None,
                        "subject_label": obj.course.subject.label if obj.course and obj.course.subject else None,
                        "teacher_name": f"{obj.teacher.first_name if obj.teacher.first_name else ''} {obj.teacher.last_name if obj.teacher else ''}",
                        "room": self.get_room(obj),
                        "name": obj.name,
                        "started_at": obj.started_at.strftime('%H:%M') if obj.started_at else None,
                        "ended_at": obj.ended_at.strftime('%H:%M') if obj.ended_at else None,
                    })

        # Format the response to include lessons by date
        result = []
        for lesson_date, lessons in lesson_by_date.items():
            result.append({
                "date": lesson_date.strftime('%d-%m-%Y'),
                "lessons": lessons
            })

        return result


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


class ExtraLessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExtraLesson
        fields = [
            'id',
            'student',
            'date',
            'teacher',
            'started_at',
            'ended_at',
            'room',
            'comment',
            'creator',
            'is_payable',
            'is_attendance',
            'created_at'
        ]


class ExtraLessonGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExtraLessonGroup
        fields = [
            'id',
            'group',
            'date',
            'started_at',
            'ended_at',
            'comment',
            'creator',
            'is_payable',
            'is_attendance',
            'created_at',
        ]


from rest_framework import serializers
from .models import ExtraLesson, ExtraLessonGroup


class CombinedExtraLessonSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    type = serializers.CharField()
    date = serializers.DateField()
    started_at = serializers.TimeField()
    ended_at = serializers.TimeField()
    comment = serializers.CharField(allow_null=True, required=False)
    creator = serializers.PrimaryKeyRelatedField(read_only=True)
    is_payable = serializers.BooleanField()
    is_attendance = serializers.BooleanField()

    # Fields specific to ExtraLesson
    student = serializers.PrimaryKeyRelatedField(read_only=True, allow_null=True)
    teacher = serializers.PrimaryKeyRelatedField(read_only=True, allow_null=True)
    room = serializers.PrimaryKeyRelatedField(read_only=True, allow_null=True)

    # Fields specific to ExtraLessonGroup
    group = serializers.PrimaryKeyRelatedField(read_only=True, allow_null=True)

    def to_representation(self, instance):
        """Convert the model instance into the combined format"""
        if isinstance(instance, ExtraLesson):
            return {
                "id": instance.id,
                "type": "individual",
                "date": instance.date,
                "started_at": instance.started_at,
                "ended_at": instance.ended_at,
                "comment": instance.comment,
                "creator": instance.creator.id if instance.creator else None,
                "is_payable": instance.is_payable,
                "is_attendance": instance.is_attendance,
                "student":  StudentSerializer(instance.student).data if instance.student else None,
                "teacher": UserSerializer(instance.teacher).data if instance.teacher else None,
                "room": RoomsSerializer(instance.room).data if instance.room else None,
                "group": None,  # Not applicable for individual lessons
            }
        elif isinstance(instance, ExtraLessonGroup):
            return {
                "id": instance.id,
                "type": "group",
                "date": instance.date,
                "started_at": instance.started_at,
                "ended_at": instance.ended_at,
                "comment": instance.comment,
                "creator": instance.creator.id if instance.creator else None,
                "is_payable": instance.is_payable,
                "is_attendance": instance.is_attendance,
                "student": None,  # Not applicable for group lessons
                "teacher": None,
                "room": None,
                "group": GroupSerializer(instance.group).data if instance.group else None,
            }
        return super().to_representation(instance)
