from datetime import date

from django.db.models import Q
from icecream import ic
from rest_framework import serializers

from .models import Attendance
from ..groups.models import Group
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
            "amount",
            'created_at',
            'updated_at',
        ]

    def get_teacher(self, obj):
        return obj.group.teacher.full_name

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

class AttendanceBulkSerializer(serializers.ModelSerializer):
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
            "amount",
            'created_at',
            'updated_at',
        ]

    def get_teacher(self, obj):
        return obj.group.teacher.full_name

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
        # This allows both single and list payloads to be processed safely
        if isinstance(validated_data, list):
            instances = []
            for item in validated_data:
                # Re-run validation for each item
                serializer = AttendanceSerializer(data=item, context=self.context)
                serializer.is_valid(raise_exception=True)
                instance = serializer.save()
                instances.append(instance)
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


