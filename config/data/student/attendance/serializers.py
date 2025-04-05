from datetime import date

from django.db.models import Q
from rest_framework import serializers

from .models import Attendance
from ..student.models import Student
from ..student.serializers import StudentSerializer
from ..subject.models import Theme
from ..subject.serializers import ThemeSerializer
from ...lid.new_lid.models import Lid
from ...lid.new_lid.serializers import LidSerializer


from django.utils.timezone import now
from rest_framework import serializers

class AttendanceSerializer(serializers.ModelSerializer):
    theme = serializers.PrimaryKeyRelatedField(queryset=Theme.objects.all(), many=True)
    lid = serializers.PrimaryKeyRelatedField(queryset=Lid.objects.all(), allow_null=True)
    student = serializers.PrimaryKeyRelatedField(queryset=Student.objects.all(), allow_null=True)
    teacher = serializers.SerializerMethodField()

    class Meta:
        model = Attendance
        fields = [
            'id',
            'theme',
            'repeated',
            'group',
            'lid',
            'student',
            'teacher',
            'reason',
            'remarks',
            'created_at',
            'updated_at',
        ]

    def get_teacher(self, obj):
        if obj.theme.exists():
            theme = obj.theme.first()
            teacher = (Attendance.objects
                       .filter(student=obj.student, theme=theme)
                       .values('theme__course__group__teacher__first_name',
                               'theme__course__group__teacher__last_name'))
            if teacher.exists():
                return teacher[0]
        return None


    def validate(self, data):
        """
        Ensure that a student or lid can only have one attendance per group per day.
        """
        student = data.get('student', None)
        lid = data.get('lid', None)
        group = data.get('group', None)
        today = now().date()

        if not student and not lid:
            raise serializers.ValidationError("Either 'student' or 'lid' must be provided.")

        instance_id = self.instance.id if self.instance else None  # Get existing instance ID if updating

        # Check if attendance exists for student (excluding the current record in updates)
        if student:
            existing_attendance = Attendance.objects.filter(
                student=student, group=group, created_at__date=today
            ).exclude(id=instance_id).exists()

            if existing_attendance:
                raise serializers.ValidationError("This student has already been marked present today in this group.")

        # Check if attendance exists for lid (excluding the current record in updates)
        if lid:
            existing_attendance = Attendance.objects.filter(
                lid=lid, group=group, created_at__date=today
            ).exclude(id=instance_id).exists()

            if existing_attendance:
                raise serializers.ValidationError("This lid has already been marked present today in this group.")

        return data

    def create(self, validated_data):
        # Handle bulk creation manually
        if isinstance(validated_data, list):
            instances = [Attendance.objects.create(**item) for item in validated_data]
            return instances
        return super().create(validated_data)


    def to_representation(self, instance):
        rep = super().to_representation(instance)

        rep['theme'] = ThemeSerializer(instance.theme, context=self.context, many=True).data
        if instance.lid:
            rep['lid'] = LidSerializer(instance.lid, context=self.context).data
        else:
            rep.pop('lid', None)

        if instance.student:
            rep['student'] = StudentSerializer(instance.student, context=self.context).data
        else:
            rep.pop('student', None)

        filtered_data = {key: value for key, value in rep.items() if value not in [{}, [], None, "", False]}
        return filtered_data


class AttendanceTHSerializer(serializers.ModelSerializer):
    theme = serializers.PrimaryKeyRelatedField(queryset=Theme.objects.all(), many=True)

    class Meta:
        model = Attendance
        fields = [
            'id',
            'theme',
            'repeated',
            'group',
            'created_at',
            'updated_at',
        ]


    def to_representation(self, instance):
        rep = super().to_representation(instance)

        rep['theme'] = ThemeSerializer(instance.theme, many=True,context=self.context).data
        filtered_data = {key: value for key, value in rep.items() if value not in [{}, [], None, "", False]}
        return filtered_data


