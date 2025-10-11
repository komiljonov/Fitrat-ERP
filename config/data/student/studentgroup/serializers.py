from datetime import date

from django.db import transaction
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from data.upload.serializers import FileUploadSerializer

from data.student.studentgroup.models import StudentGroup, SecondaryStudentGroup
from data.student.groups.models import Group, SecondaryGroup, GroupSaleStudent
from data.student.groups.serializers import (
    SecondaryGroupSerializer,
    GroupSaleStudentSerializer,
)
from data.student.student.models import Student
from data.student.student.serializers import StudentSerializer
from data.account.serializers import UserSerializer
from data.lid.new_lid.models import Lid
from data.lid.new_lid.serializers import LeadSerializer


class StudentsGroupSerializer(serializers.ModelSerializer):
    group = serializers.PrimaryKeyRelatedField(
        queryset=Group.objects.all(),
        required=True,
    )
    student = serializers.PrimaryKeyRelatedField(
        queryset=Student.objects.all(),
        allow_null=True,
        required=False,
    )
    lid = serializers.PrimaryKeyRelatedField(
        queryset=Lid.objects.all(),
        allow_null=True,
        required=False,
    )

    lesson_count = serializers.SerializerMethodField()
    # current_theme = serializers.SerializerMethodField()
    group_price = serializers.SerializerMethodField()

    class Meta:
        model = StudentGroup
        fields = [
            "id",
            "group",
            "lid",
            "student",
            "price",
            "price_comment",
            "homework_type",
            "lesson_count",
            # "current_theme",
            "group_price",
            "is_archived",
        ]
        validators = [
            UniqueTogetherValidator(
                queryset=StudentGroup.objects.all(),
                fields=["group", "student"],
                message="O'quvchi ushbu guruhda allaqachon mavjud!",
            ),
            UniqueTogetherValidator(
                queryset=StudentGroup.objects.all(),
                fields=["group", "lid"],
                message="Lid ushbu guruhda allaqachon mavjud!",
            ),
        ]

    # ---- Derived fields (use annotations / batched queries) ----
    def get_group_price(self, obj):
        """
        Returns sale for (group, student) or (group, lid).
        We batch fetch in the list view using in-memory cache on the serializer context
        to avoid N+1 queries. Fallback to a single query if not present.
        """
        cache = self.context.get("_sale_cache")
        key = (obj.group_id, obj.student_id or f"LID:{obj.lid_id}")
        sale = cache.get(key) if cache else None
        if sale is None:
            qs = GroupSaleStudent.objects.filter(group=obj.group)
            if obj.student_id:
                qs = qs.filter(student_id=obj.student_id)
            elif obj.lid_id:
                qs = qs.filter(lid_id=obj.lid_id)
            sale = qs.first()
        return (
            GroupSaleStudentSerializer(sale, context=self.context).data
            if sale
            else None
        )

    # def get_current_theme(self, obj):
    #     """
    #     Themes taken today for this group (deduped).
    #     Use a single per-request cache keyed by group_id to avoid N+1.
    #     """
    #     cache = self.context.get("_today_theme_cache")
    #     items = cache.get(obj.group_id) if cache else None
    #     if items is None:
    #         items = list(
    #             Attendance.objects.filter(
    #                 group_id=obj.group_id, created_at__date=date.today()
    #             )
    #             .values("theme", "repeated")
    #             .distinct()
    #         )
    #     return items

    def get_lesson_count(self, obj):
        """
        Use DB annotations if available; fall back to safe defaults.
        """
        total = getattr(obj, "total_lessons", None)
        attended = getattr(obj, "attended_lessons", None)
        return {"lessons": total or 0, "attended": attended or 0}

    # ---- Validation ----
    def validate(self, attrs):
        # support PATCH: merge attrs with instance
        student = (
            attrs.get("student")
            if "student" in attrs
            else getattr(self.instance, "student", None)
        )
        lid = (
            attrs.get("lid") if "lid" in attrs else getattr(self.instance, "lid", None)
        )

        if bool(student) == bool(lid):  # both set or both empty
            raise serializers.ValidationError(
                {"detail": "Faqat bittasi to‘ldirilishi kerak: student yoki lid."}
            )
        return attrs

    # ---- Create ----
    @transaction.atomic
    def create(self, validated_data):
        filial = validated_data.pop("filial", None)
        if not filial:
            request = self.context.get("request")
            if request and hasattr(request.user, "filial"):
                filial = request.user.filial.first()
        if not filial:
            raise serializers.ValidationError(
                {"filial": "Filial could not be determined."}
            )

        return StudentGroup.objects.create(filial=filial, **validated_data)

    # ---- Output shaping ----
    def to_representation(self, instance: StudentGroup):
        rep = super().to_representation(instance)

        if instance.group:
            subject = instance.group.course.subject if instance.group.course else None
            subject_data = (
                {
                    "name": subject.name,
                    "image": (
                        FileUploadSerializer(subject.image, context=self.context).data
                        if getattr(subject, "image", None)
                        else None
                    ),
                }
                if subject
                else None
            )

            rep["group"] = {
                "group_id": instance.group.id,
                "group_name": instance.group.name,
                "start_date": (
                    instance.group.start_date.strftime("%d/%m/%Y, %H:%M:%S")
                    if instance.group.start_date
                    else None
                ),
                "level": getattr(getattr(instance.group, "level", None), "id", None),
                "subject": subject_data,
                "course": getattr(
                    getattr(instance.group, "course", None), "name", None
                ),
                "price": instance.group.price,
                "teacher": getattr(
                    getattr(instance.group, "teacher", None), "full_name", None
                ),
                "room_number": getattr(
                    getattr(instance.group, "room_number", None), "room_number", None
                ),
                "course_id": getattr(
                    getattr(instance.group, "course", None), "id", None
                ),
                "finish_date": instance.group.finish_date,
            }
        else:
            rep.pop("group", None)

        if instance.lid:
            rep["lid"] = LeadSerializer(
                instance.lid,
                context=self.context,
                include_only=[
                    "id",
                    "first_name",
                    "last_name",
                    "middle_name",
                    "phone_number",
                    "teacher",
                    # "group",
                    "sales_manager",
                    "service_manager",
                    "balance",
                ],
            ).data
        else:
            rep.pop("lid", None)

        if instance.student:
            rep["student"] = StudentSerializer(
                instance.student,
                context=self.context,
                include_only=[
                    "id",
                    "first_name",
                    "last_name",
                    "middle_name",
                    "phone",
                    "teacher",
                    "sales_manager",
                    "service_manager",
                    "learning",
                    "balance",
                ],
            ).data
        else:
            rep.pop("student", None)

        # prune empties
        return {k: v for k, v in rep.items() if v not in ({}, None, "", False)}


class StudentGroupMixSerializer(serializers.ModelSerializer):
    # group = serializers.PrimaryKeyRelatedField(queryset=Group.objects.all())
    student = serializers.PrimaryKeyRelatedField(queryset=Student.objects.all())
    lid = serializers.PrimaryKeyRelatedField(queryset=Lid.objects.all())

    class Meta:
        model = StudentGroup
        fields = [
            "id",
            "group",
            "student",
            "lid",
        ]

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        # rep['group'] = GroupSerializer(instance.group).data
        rep["student"] = StudentSerializer(instance.student).data
        rep["lid"] = LeadSerializer(instance.lid).data
        return rep


class SecondaryStudentsGroupSerializer(serializers.ModelSerializer):
    group = serializers.PrimaryKeyRelatedField(
        queryset=SecondaryGroup.objects.all(),
        required=True,
    )
    student = serializers.PrimaryKeyRelatedField(
        queryset=Student.objects.all(),
        allow_null=True,
    )
    lid = serializers.PrimaryKeyRelatedField(
        queryset=Lid.objects.all(),
        allow_null=True,
    )
    main_teacher = serializers.SerializerMethodField()

    class Meta:
        model = SecondaryStudentGroup
        fields = ["id", "group", "lid", "main_teacher", "student"]

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

        room = SecondaryStudentGroup.objects.create(filial=filial, **validated_data)
        return room

    def get_main_teacher(self, instance):
        teacher = getattr(instance.group, "teacher", None)
        return UserSerializer(teacher).data if teacher else None

    def validate_group(self, value):
        if not SecondaryGroup.objects.filter(id=value.id).exists():
            raise serializers.ValidationError("Invalid group ID")
        return value

    def validate_student(self, value):
        if not Student.objects.filter(id=value.id).exists():
            raise serializers.ValidationError("Invalid student ID")
        return value

    def validate_lid(self, value):
        if value and not Lid.objects.filter(id=value.id).exists():
            raise serializers.ValidationError("Invalid lid ID")
        return value

    def to_representation(self, instance):
        rep = super().to_representation(instance)

        rep["group"] = SecondaryGroupSerializer(
            instance.group, context=self.context
        ).data
        rep["lid"] = (
            LeadSerializer(instance.lid, context=self.context).data
            if instance.lid
            else None
        )
        rep["student"] = (
            StudentSerializer(instance.student, context=self.context).data
            if instance.student
            else None
        )

        return {
            key: value
            for key, value in rep.items()
            if value not in [{}, [], None, "", False]
        }


class StudentGroupUpdateSerializer(serializers.Serializer):

    group = serializers.PrimaryKeyRelatedField(queryset=Group.objects.all())
    add_group = serializers.PrimaryKeyRelatedField(queryset=StudentGroup.objects.all())

    student = serializers.PrimaryKeyRelatedField(
        queryset=Student.objects.all(),
        required=False,
        allow_null=True,
    )

    order = serializers.PrimaryKeyRelatedField(
        queryset=Lid.objects.all(),
        required=False,
        allow_null=True,
    )

    def validate(self, attrs):
        student = attrs.get("student")
        order = attrs.get("order")

        # Require exactly one of them
        if bool(student) == bool(order):
            # This means both are filled or both are empty
            raise serializers.ValidationError(
                "Either 'student' or 'order' must be provided, but not both."
            )

        if student != None:
            self.custom_validate_student(attrs)

        if order != None:
            self.custom_validate_order(attrs)

        return attrs

    def custom_validate_student(self, attrs):

        student: Student = attrs["student"]

        if student.groups.filter(group=attrs["group"]).exists():
            raise serializers.ValidationError(
                "Can't  add students group to already existing  one."
            )

    def custom_validate_order(self, attrs):

        order: Lid = attrs["order"]

        if order.groups.filter(group=attrs["group"]).exists():
            raise serializers.ValidationError(
                "Can't  add students group to already existing  one."
            )


{
    "student_group": "6e1d9a6c-7bf4-4b6a-b728-7c0d0c215a3c",
    "amount": 6002,
    "comment": "AAABBB",
}
