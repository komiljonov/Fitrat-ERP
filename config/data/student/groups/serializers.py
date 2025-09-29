from datetime import date

from django.db.models import Count, Q
from rest_framework import serializers

from .lesson_date_calculator import calculate_lessons
from .models import Group, Day, Room, SecondaryGroup, GroupSaleStudent
from .room_filings_calculate import calculate_room_filling_statistics
from data.student.attendance.models import Attendance, SecondaryAttendance
from data.student.course.models import Course
from data.student.course.serializers import CourseSerializer
from data.student.student.models import Student
from data.student.studentgroup.models import StudentGroup, SecondaryStudentGroup
from data.student.subject.models import Theme, Level
from data.student.subject.serializers import LevelSerializer
from data.account.models import CustomUser
from data.account.serializers import UserSerializer
from data.lid.new_lid.models import Lid


class DaySerializer(serializers.ModelSerializer):
    class Meta:
        model = Day
        fields = [
            "id",
            "name",
        ]


class GroupSerializer(serializers.ModelSerializer):
    teacher = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())
    scheduled_day_type = serializers.PrimaryKeyRelatedField(
        queryset=Day.objects.all(), many=True
    )
    student_count = serializers.SerializerMethodField()
    lessons_count = serializers.SerializerMethodField()
    current_theme = serializers.SerializerMethodField()
    room_number = serializers.PrimaryKeyRelatedField(
        queryset=Room.objects.all(), allow_null=True
    )
    course = serializers.PrimaryKeyRelatedField(
        queryset=Course.objects.all(), allow_null=True
    )
    subject = serializers.SerializerMethodField()
    level = serializers.PrimaryKeyRelatedField(
        queryset=Level.objects.all(), allow_null=True
    )
    real_student = serializers.SerializerMethodField()

    class Meta:
        model = Group
        fields = [
            "id",
            "name",
            "teacher",
            "secondary_teacher",
            "status",
            "course",
            "subject",
            "level",
            "student_count",
            "lessons_count",
            "room_number",
            # "price_type",
            "price",
            "scheduled_day_type",
            "comment",
            "started_at",
            "ended_at",
            "start_date",
            "finish_date",
            "real_student",
            "is_secondary",
            "is_archived",
            "current_theme",
            "created_at",
        ]

    def __init__(self, *args, **kwargs):
        fields_to_remove: list | None = kwargs.pop("remove_fields", None)
        include_only: list | None = kwargs.pop("include_only", None)

        if fields_to_remove and include_only:
            raise ValueError(
                "You cannot use 'remove_fields' and 'include_only' at the same time."
            )

        super(GroupSerializer, self).__init__(*args, **kwargs)

        if include_only is not None:
            allowed = set(include_only)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)

        elif fields_to_remove:
            for field_name in fields_to_remove:
                self.fields.pop(field_name, None)

    def get_real_student(self, obj):
        student_count = StudentGroup.objects.filter(
            Q(group=obj) & (Q(student__is_archived=False) | Q(lid__is_archived=False)),
            is_archived=False,
        ).count()

        first = StudentGroup.objects.filter(
            Q(group=obj)
            & (
                Q(student__isnull=True)
                | Q(
                    lid__lid_stage_type="ORDERED_LID",
                    lid__ordered_stages="BIRINCHI_DARS_BELGILANGAN",
                )
            )
        ).count()

        return student_count - first

    def get_subject(self, obj):
        return (
            Group.objects.filter(pk=obj.pk)
            .values("course__subject", "course__subject__name")
            .first()
        )

    def get_current_theme(self, obj):
        today = date.today()

        # Ensures we compare only the date and remove duplicate themes
        attendance = (
            Attendance.objects.filter(group=obj, created_at__date=today)
            .values("theme", "repeated")
            .distinct()  # Remove duplicates
        )

        return list(attendance)

    def get_lessons_count(self, obj: Group):
        total_lessons = Theme.objects.filter(
            course=obj.course,
            level=obj.level,
            is_archived=False,
        ).count()

        attended_lessons = (
            Attendance.objects.filter(
                group=obj,
            )
            .values("theme")  # Group by lesson
            .annotate(attended_count=Count("id"))  # Count attendance per lesson
            .count()  # Count unique lessons with attendance records
        )

        return {
            "lessons": total_lessons,  # Total lessons in the group
            "attended": attended_lessons,  # Lessons that have attendance records
        }

    def get_student_count(self, obj):

        student_count = StudentGroup.objects.filter(
            Q(group=obj, is_archived=False)
            & (Q(student__is_archived=False) | Q(lid__is_archived=False))
        ).count()

        return student_count

    def to_representation(self, instance):
        res = super().to_representation(instance)
        if "level" in res:
            res["level"] = LevelSerializer(
                instance.level, context=self.context, include_only=["id", "name"]
            ).data

        if "teacher" in res:
            res["teacher"] = UserSerializer(
                instance.teacher,
                context=self.context,
                include_only=["id", "first_name", "last_name", "full_name"],
            ).data

        if "room_number" in res:
            res["room_number"] = RoomsSerializer(
                instance.room_number,
                context=self.context,
            ).data

        if "course" in res:
            res["course"] = CourseSerializer(
                instance.course,
                context=self.context,
                include_only=["id", "name"],
            ).data

        return res

    def create(self, validated_data):
        status = validated_data.pop("status", None)
        scheduled_day_type_data = validated_data.pop("scheduled_day_type", [])
        filial = validated_data.pop("filial", None)

        if not filial:
            request = self.context.get("request")
            if request and hasattr(request.user, "filial"):
                filial = request.user.filial.first()

        if not filial:
            raise serializers.ValidationError(
                {"filial": "Filial could not be determined."}
            )

        # if not status:
        #     group_type = Group_Type.objects.filter().first()
        #     if group_type:
        #         status = group_type.price_type
        #         validated_data["status"] = status

        # ✅ Ensure course exists
        course = validated_data.get("course")
        if not course:
            raise serializers.ValidationError({"course": "This field is required."})

        # ✅ Create the group
        group = Group.objects.create(filial=filial, **validated_data)

        # ✅ Set related ManyToMany data
        group.scheduled_day_type.set(scheduled_day_type_data)

        return group


class GroupLessonSerializer(serializers.ModelSerializer):
    group_lesson_dates = serializers.SerializerMethodField()  # Add this field

    class Meta:
        model = Group
        fields = [
            "id",
            "name",
            "teacher",
            "status",
            "room_number",
            # "price_type",
            "course",
            "price",
            "scheduled_day_type",
            "comment",
            "started_at",
            "ended_at",
            "start_date",
            "finish_date",
            "group_lesson_dates",  # Include the new field
        ]

    def get_group_lesson_dates(self, obj):
        """
        Calculate lesson dates based on the group data.
        """
        # Retrieve required data from the Group instance
        start_date = obj.start_date.strftime("%Y-%m-%d") if obj.start_date else None
        end_date = obj.finish_date.strftime("%Y-%m-%d") if obj.finish_date else None
        print(end_date)

        # If the lesson type is a Many-to-Many field, get the weekday names
        lesson_days_queryset = (
            obj.scheduled_day_type.all()
        )  # This retrieves the related days
        lesson_days = [
            day.name for day in lesson_days_queryset
        ]  # Assuming 'name' stores the weekday name (e.g., 'Monday')

        holidays = [
            ""
        ]  # Replace with actual logic to fetch holidays, e.g., from another model
        days_off = ["Yakshanba"]  # Replace or fetch from settings/config

        if start_date and end_date:
            # Use the calculate_lessons function to get lesson dates
            lesson_dates = calculate_lessons(
                start_date,
                end_date,
                ",".join(lesson_days),
                holidays,
                days_off,
            )
            return lesson_dates
        return []


class RoomsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = [
            "id",
            "room_number",
            "room_filling",
            "created_at",
            "updated_at",
        ]

    def create(self, validated_data):
        filial = validated_data.pop("filial", None)
        if not filial:
            request = self.context.get("request")  #
            if request and hasattr(request.user, "filial"):
                filial = request.user.filial.first()

        if not filial:
            raise serializers.ValidationError(
                {"filial": "Filial could not be determined."}
            )

        room = Room.objects.create(filial=filial, **validated_data)
        return room


class RoomFilterSerializer(serializers.ModelSerializer):
    lessons_start_time = serializers.CharField()
    lessons_end_time = serializers.CharField()
    average_lesson_hours = serializers.CharField()

    class Meta:
        model = Room
        fields = [
            "id",
            "room_number",
            "room_filling",
            "created_at",
            "updated_at",
            "lessons_start_time",  # Include here
            "lessons_end_time",  # Include here
            "average_lesson_hours",  # Include here
        ]

    def calculate(self, validated_data):
        lessons_start_time = validated_data.pop("lessons_start_time", None)
        lessons_end_time = validated_data.pop("lessons_end_time", None)
        average_lesson_hours = validated_data.pop("average_lesson_hours", 2)

        lessons_start_time = (
            lessons_start_time.strftime("%H:%M") if lessons_start_time else "08:00"
        )
        lessons_end_time = (
            lessons_end_time.strftime("%H:%M") if lessons_end_time else "20:00"
        )

        average_students_filling = calculate_room_filling_statistics(
            room_id=validated_data.get("id"),
            lessons_start_time=lessons_start_time,
            lessons_end_time=lessons_end_time,
            lesson_duration=average_lesson_hours,
        )

        return average_students_filling


class SecondaryGroupListSerializer(serializers.ListSerializer):
    def create(self, validated_data):
        instances = [self.child.create(attrs) for attrs in validated_data]
        return SecondaryGroup.objects.bulk_create(instances)


class SecondaryGroupSerializer(serializers.ModelSerializer):
    group = serializers.PrimaryKeyRelatedField(queryset=Group.objects.all())
    teacher = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())
    student_count = serializers.SerializerMethodField()
    current_theme = serializers.SerializerMethodField()

    class Meta:
        model = SecondaryGroup
        fields = [
            "id",
            "name",
            "group",
            "teacher",
            "scheduled_day_type",
            "status",
            "student_count",
            "current_theme",
            "started_at",
            "ended_at",
            "start_date",
            "finish_date",
            "created_at",
            "updated_at",
        ]
        list_serializer_class = SecondaryGroupListSerializer

    def get_current_theme(self, obj):
        today = date.today()
        attendance = (
            SecondaryAttendance.objects.filter(group=obj, created_at__date=today)
            .values(
                "theme",
            )
            .distinct()
        )
        return list(attendance)

    def get_student_count(self, obj):
        return SecondaryStudentGroup.objects.filter(
            Q(group=obj) & (Q(student__is_archived=False) | Q(lid__is_archived=False))
        ).count()

    def create(self, validated_data):
        scheduled_day_types = validated_data.pop("scheduled_day_type", [])
        filial = validated_data.pop("filial", None)

        request = self.context.get("request")
        if not filial and request and hasattr(request.user, "filial"):
            filial = request.user.filial.first()

        if not filial:
            raise serializers.ValidationError(
                {"filial": "Filial could not be determined."}
            )

        group = SecondaryGroup.objects.create(filial=filial, **validated_data)

        if scheduled_day_types:
            group.scheduled_day_type.set(scheduled_day_types)

        return group

    def update(self, instance, validated_data):
        scheduled_day_types = validated_data.pop("scheduled_day_type", None)
        instance = super().update(instance, validated_data)
        if scheduled_day_types is not None:
            instance.scheduled_day_type.set(scheduled_day_types)
        return instance

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["teacher"] = UserSerializer(instance.teacher).data
        rep["group"] = GroupSerializer(instance.group).data
        return rep


class SecondaryGroupModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = SecondaryGroup
        fields = ["id", "name"]


class GroupSaleStudentSerializer(serializers.ModelSerializer):
    student = serializers.PrimaryKeyRelatedField(
        queryset=Student.objects.all(), allow_null=True
    )
    lid = serializers.PrimaryKeyRelatedField(
        queryset=Lid.objects.all(), allow_null=True
    )

    class Meta:
        model = GroupSaleStudent
        fields = ["id", "group", "student", "lid", "amount", "comment"]

    
    def validate(self, attrs):
        student = attrs.get("student")
        lid = attrs.get("lid")
        if not student and not lid:
            raise serializers.ValidationError(
                "Either 'student' or 'lid' must be provided."
            )
        return attrs

class CheckRoomTeacherConflictSerializer(serializers.Serializer):

    room = serializers.PrimaryKeyRelatedField(queryset=Room.objects.all())
    date = serializers.DateField()
    started_at = serializers.TimeField()
    ended_at = serializers.TimeField()

    teacher = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.filter(role="TEACHER")
    )

    scheduled_day_type = serializers.PrimaryKeyRelatedField(
        queryset=Day.objects.all(), many=True
    )

    course = serializers.PrimaryKeyRelatedField(queryset=Course.objects.all())

    level = serializers.PrimaryKeyRelatedField(queryset=Level.objects.all())
