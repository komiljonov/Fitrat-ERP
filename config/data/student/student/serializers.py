import datetime
import hashlib

from django.db.models import F, Avg
from django.utils.module_loading import import_string
from icecream import ic
from rest_framework import serializers

from .models import Student, FistLesson_data
from ..attendance.models import Attendance
from ..groups.lesson_date_calculator import calculate_lessons
from ..groups.models import Group
from ..homeworks.models import Homework_history
from ..mastering.models import Mastering
from ..studentgroup.models import StudentGroup, SecondaryStudentGroup
from ..subject.models import Level
from ...account.models import CustomUser
from ...account.serializers import UserSerializer
from ...department.filial.models import Filial
from ...department.filial.serializers import FilialSerializer
from ...department.marketing_channel.models import MarketingChannel
from ...department.marketing_channel.serializers import MarketingChannelSerializer
from ...finances.finance.models import SaleStudent, VoucherStudent
from ...parents.models import Relatives
from ...upload.models import File
from ...upload.serializers import FileUploadSerializer


class StudentSerializer(serializers.ModelSerializer):
    photo = serializers.PrimaryKeyRelatedField(
        queryset=File.objects.all(), allow_null=True
    )
    filial = serializers.PrimaryKeyRelatedField(
        queryset=Filial.objects.all(), allow_null=True
    )
    marketing_channel = serializers.PrimaryKeyRelatedField(
        queryset=MarketingChannel.objects.all(), allow_null=True
    )
    course = serializers.SerializerMethodField()
    group = serializers.SerializerMethodField()
    relatives = serializers.SerializerMethodField()
    file = serializers.PrimaryKeyRelatedField(
        queryset=File.objects.all(), many=True, allow_null=True
    )
    password = serializers.CharField(write_only=True, required=False, allow_null=True)
    attendance_count = serializers.SerializerMethodField()
    is_attendance = serializers.SerializerMethodField()
    secondary_group = serializers.SerializerMethodField()
    secondary_teacher = serializers.SerializerMethodField()
    learning = serializers.SerializerMethodField()
    teacher = serializers.SerializerMethodField()
    sales = serializers.SerializerMethodField()
    voucher = serializers.SerializerMethodField()
    is_passed = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        fields_to_remove: list | None = kwargs.pop("remove_fields", None)
        include_only: list | None = kwargs.pop("include_only", None)

        if fields_to_remove and include_only:
            raise ValueError(
                "You cannot use 'remove_fields' and 'include_only' at the same time."
            )

        super(StudentSerializer, self).__init__(*args, **kwargs)

        if include_only is not None:
            allowed = set(include_only)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)

        elif fields_to_remove:
            for field_name in fields_to_remove:
                self.fields.pop(field_name, None)

    class Meta:
        model = Student
        fields = [
            "id",
            "photo",
            "first_name",
            "last_name",
            "middle_name",
            "is_attendance",
            "phone",
            "is_frozen",
            "learning",
            "password",
            "date_of_birth",
            "education_lang",
            "student_type",
            "edu_class",
            "edu_level",
            "subject",
            "sales",
            "voucher",
            "ball",
            "filial",
            "marketing_channel",
            "student_stage_type",
            "balance_status",
            "balance",
            "service_manager",
            "course",
            "group",
            "teacher",
            "call_operator",
            "sales_manager",
            "is_archived",
            "is_frozen",
            "attendance_count",
            "relatives",
            "file",
            "is_passed",
            "secondary_group",
            "secondary_teacher",
            "new_student_stages",
            "new_student_date",
            "active_date",
            "created_at",
            "updated_at",
        ]

    def get_is_passed(self, obj):
        request = self.context.get("request")
        if not request:
            return False

        homework_id = request.query_params.get("homework")
        if not homework_id:
            return False

        homeworks = Homework_history.objects.filter(
            homework__id=homework_id,
            student=obj,
            status="Passed",
            is_active=True,
            created_at__gt=datetime.datetime.today(),
            created_at__lte=datetime.datetime.today() + datetime.timedelta(days=2),
        )

        return homeworks.exists()

    def get_voucher(self, obj):
        voucher = VoucherStudent.objects.filter(student=obj)
        if voucher:
            return [
                {
                    "id": voucher.voucher.id,
                    "amount": voucher.voucher.amount,
                    "is_expired": voucher.voucher.is_expired,
                    "created_at": voucher.created_at,
                }
                for voucher in voucher
            ]

    def get_sales(self, obj):
        sales = SaleStudent.objects.filter(student__id=obj.id)
        return [
            {
                "id": sale.sale.id,
                "amount": sale.sale.amount,
                "sale_status": sale.sale.status,
                "date": (
                    sale.expire_date.strftime("%Y-%m-%d")
                    if sale.expire_date
                    else "Unlimited"
                ),
            }
            for sale in sales
        ]

    def get_teacher(self, obj):
        group = (
            StudentGroup.objects.filter(student=obj)
            .select_related("group__teacher")
            .first()
        )
        if group and group.group and group.group.teacher:
            teacher = group.group.teacher
            return {"id": teacher.id, "full_name": teacher.full_name}
        return None

    def get_learning(self, obj):
        mastering_qs = Mastering.objects.filter(student=obj)

        if not mastering_qs.exists():  # If no records, return default values
            return {
                "score": 1,  # Default lowest score
                "learning": 0,  # Default lowest percentage
            }

        # Calculate the average score from 1 to 5
        average_score = mastering_qs.aggregate(avg_ball=Avg("ball"))["avg_ball"] or 0

        # Scale the score between 1 to 5 (assuming 0-100 scores exist)
        score_scaled = min(
            max(round(average_score / 20), 1), 5
        )  # Ensure it's between 1 to 5

        # Scale the percentage between 1 to 100
        percentage_scaled = min(max(round((average_score / 100) * 100), 0), 100)

        return {"score": score_scaled, "learning": percentage_scaled}

    def get_is_attendance(self, obj):
        # Prefetch only related scheduled_day_type once
        groups = (
            StudentGroup.objects.filter(student=obj)
            .select_related("group")  # ensures group exists
            .prefetch_related("group__scheduled_day_type")
        )

        today = datetime.date.today()
        end_date = today + datetime.timedelta(days=30)

        start_date_str = today.strftime("%Y-%m-%d")
        end_date_str = end_date.strftime("%Y-%m-%d")

        for group in groups:
            group_obj = getattr(group, "group", None)
            if not group_obj:
                continue

            # Get lesson days
            scheduled_days = getattr(group_obj, "scheduled_day_type", None)
            if not scheduled_days:
                continue

            lesson_days = [day.name for day in scheduled_days.all()]
            if not lesson_days:
                continue

            # Calculate lesson dates
            lesson_dates = calculate_lessons(
                start_date=start_date_str,
                end_date=end_date_str,
                lesson_type=",".join(lesson_days),
                holidays=[""],
                days_off=["Yakshanba"],
            )

            if lesson_dates:
                # If any attendance date found, return True
                return True

        return False

    def get_secondary_group(self, obj):
        group = (
            SecondaryStudentGroup.objects.filter(student=obj)
            .select_related("group")
            .only("id", "group__name")
            .first()
        )

        if group and group.group:
            return {"id": group.id, "name": group.group.name}

        return None

    def get_secondary_teacher(self, obj):
        group = (
            SecondaryStudentGroup.objects.filter(student=obj)
            .select_related("group__teacher")
            .first()
        )

        if group and group.group and group.group.teacher:
            teacher = group.group.teacher
            return {
                "id": teacher.id,
                "first_name": teacher.first_name,
                "last_name": teacher.last_name,
            }

        return None

    def get_course(self, obj):
        courses = StudentGroup.objects.filter(student=obj).values(
            "group__course__name", "group__course__level__name"
        )
        return list(courses)

    def get_group(self, obj: Student):

        # courses = (StudentGroup.objects.filter(student=obj)
        courses = obj.students_group.values(
            "group__name",
            "group__status",
            "group__started_at",
            "group__ended_at",
            "group__teacher__first_name",
            "group__teacher__last_name",
        ).distinct()
        return list(courses)

    def get_relatives(self, obj):
        relative = Relatives.objects.filter(student=obj).values("name", "phone", "who")
        return list(relative)

    def get_attendance_count(self, obj):
        attendance = Attendance.objects.filter(student=obj)
        return attendance.count() + 1

    def update(self, instance, validated_data):
        password = validated_data.get("password")
        if password:  # Only set the password if it's provided
            instance.password = hashlib.sha512(password.encode("utf-8")).hexdigest()
            instance.save()

        # Handle file updates with set()
        files = validated_data.get("file", None)
        if files is not None:
            # Convert the provided list of files to a set to avoid duplicates
            instance.file.set(files)

        # Update other fields
        for attr, value in validated_data.items():
            if (
                attr != "password" and attr != "file"
            ):  # Skip the password and file fields
                setattr(instance, attr, value)

        instance.save()
        return instance

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if "photo" in representation:
            representation["photo"] = FileUploadSerializer(
                instance.photo, context=self.context
            ).data

        if "filial" in representation:
            representation["filial"] = (
                FilialSerializer(instance.filial).data if instance.filial else None
            )

        if "marketing_channel" in representation:
            representation["marketing_channel"] = (
                MarketingChannelSerializer(instance.marketing_channel).data
                if instance.marketing_channel
                else None
            )

        if "sales_manager" in representation:
            representation["sales_manager"] = (
                UserSerializer(
                    instance.sales_manager,
                    include_only=["id", "full_name", "first_name", "last_name"],
                ).data
                if instance.sales_manager
                else None
            )
        if "service_manager" in representation:
            representation["service_manager"] = (
                UserSerializer(
                    instance.service_manager,
                    include_only=["id", "full_name", "first_name", "last_name"],
                ).data
                if instance.service_manager
                else None
            )

        if "file" in representation:
            representation["file"] = FileUploadSerializer(
                instance.file.all(), many=True, context=self.context
            ).data

        return representation


class StudentAppSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = [
            "id",
            "first_name",
            "last_name",
        ]

    def get_attendance(self, obj):
        attendance = Attendance.objects.filter(lesson=obj)
        AttendanceSerializer = import_string(
            "data.student.attendance.serializers.AttendanceSerializer"
        )
        return AttendanceSerializer(attendance, many=True).data


class FistLesson_dataSerializer(serializers.ModelSerializer):
    group = serializers.PrimaryKeyRelatedField(
        queryset=Group.objects.all(), allow_null=True
    )
    teacher = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.all(), allow_null=True
    )
    level = serializers.PrimaryKeyRelatedField(
        queryset=Level.objects.all(), allow_null=True
    )

    class Meta:
        model = FistLesson_data
        fields = [
            "id",
            "group",
            "teacher",
            "lesson_date",
            "level",
            "lid",
        ]
