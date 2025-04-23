from django.utils.timezone import now
from rest_framework import serializers

from data.student.attendance.models import SecondaryAttendance
from data.student.attendance.serializers import AttendanceSerializer
from data.student.groups.models import SecondaryGroup
from data.student.student.models import Student
from data.student.student.serializers import StudentSerializer
from data.student.subject.models import Theme
from data.student.subject.serializers import ThemeSerializer


class SecondaryAttendanceSerializer(serializers.Serializer):
    student = serializers.PrimaryKeyRelatedField(queryset=Student.objects.all(),allow_null=True)
    group = serializers.PrimaryKeyRelatedField(queryset=SecondaryGroup.objects.all(),allow_null=True)
    theme = serializers.PrimaryKeyRelatedField(queryset=Theme.objects.all(),allow_null=True)

    class Meta:
        model = SecondaryAttendance
        fields = [
            "id",
            "student",
            "group",
            "theme",
            "reason",
            "remarks",
            "updated_at",
        ]
    def get_teacher(self, obj):
        return obj.group.teacher.full_name

    def validate(self, attrs):
        student = attrs.get("student")
        group = attrs.get("group")
        theme = attrs.get("theme")
        today = now().date()

        if student:
            ex_att = SecondaryAttendance.objects.filter(
                student=student,
                group=group,
                created_at__date=today
            ).exclude(id=attrs.get("id")).exists()
            if ex_att:
                raise serializers.ValidationError(
                    "Student %s is already attendanced." % student
                )
        return attrs

    def create(self, validated_data):
        # This allows both single and list payloads to be processed safely
        if isinstance(validated_data, list):
            instances = []
            for item in validated_data:
                # Re-run validation for each item
                serializer = SecondaryAttendanceSerializer(data=item, context=self.context)
                serializer.is_valid(raise_exception=True)
                instance = serializer.save()
                instances.append(instance)
            return instances
        return super().create(validated_data)

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['theme'] = ThemeSerializer(instance.theme, context=self.context, many=True).data
        rep['student'] = StudentSerializer(instance.student, context=self.context).data

        return rep