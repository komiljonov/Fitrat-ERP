from django.utils.timezone import now
from rest_framework import serializers

from data.student.attendance.models import SecondaryAttendance
from data.student.attendance.serializers import AttendanceSerializer
from data.student.groups.models import SecondaryGroup
from data.student.student.models import Student
from data.student.student.serializers import StudentSerializer
from data.student.subject.models import Theme
from data.student.subject.serializers import ThemeSerializer


class SecondaryAttendanceBulkSerializer(serializers.ListSerializer):
    def create(self, validated_data):
        ids = [item.get("id") for item in validated_data if item.get("id")]
        duplicates = set(
            SecondaryAttendance.objects.filter(id__in=ids).values_list("id", flat=True)
        )
        if duplicates:
            raise serializers.ValidationError(
                f"Duplicate ID(s) already exist: {', '.join(map(str, duplicates))}"
            )

        instances = []
        for item in validated_data:
            item.pop("id", None)  # Ensure id isn't passed if model auto-generates it
            serializer = self.child.__class__(data=item, context=self.context)
            serializer.is_valid(raise_exception=True)
            instance = serializer.save()
            instances.append(instance)
        return instances


class SecondaryAttendanceSerializer(serializers.ModelSerializer):
    student = serializers.PrimaryKeyRelatedField(queryset=Student.objects.all(), allow_null=True)
    group = serializers.PrimaryKeyRelatedField(queryset=SecondaryGroup.objects.all(), allow_null=True)
    theme = serializers.PrimaryKeyRelatedField(queryset=Theme.objects.all(), allow_null=True)

    class Meta:
        model = SecondaryAttendance
        fields = [
            "id", "student", "group", "theme", "reason",
            "remarks", "updated_at"
        ]
        list_serializer_class = SecondaryAttendanceBulkSerializer
        extra_kwargs = {
            "id": {"read_only": True}
        }

    def get_teacher(self, obj):
        return obj.group.teacher.full_name

    def validate(self, attrs):
        student = attrs.get("student")
        group = attrs.get("group")
        today = now().date()

        if student and group:
            exists = SecondaryAttendance.objects.filter(
                student=student,
                group=group,
                created_at__date=today
            ).exists()
            if exists:
                raise serializers.ValidationError(
                    f"Student {student} is already marked present today."
                )
        return attrs

    def create(self, validated_data):
        return SecondaryAttendance.objects.create(**validated_data)

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['theme'] = ThemeSerializer(instance.theme, context=self.context).data
        rep['student'] = StudentSerializer(instance.student, context=self.context).data
        return rep