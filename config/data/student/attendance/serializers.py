from datetime import datetime, time

from django.utils.timezone import now, make_aware
from rest_framework import serializers

from .models import Attendance
from ..homeworks.models import Homework_history, Homework
from ..mastering.models import Mastering
from ..quiz.models import Quiz
from ..student.models import Student
from ..student.serializers import StudentSerializer
from ..subject.models import Theme
from ..subject.serializers import ThemeSerializer
from ...lid.new_lid.models import Lid
from ...lid.new_lid.serializers import LidSerializer


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

        instance_id = self.instance.id if self.instance else None

        # Define start and end of day
        start_datetime = make_aware(datetime.combine(today, time.min))
        end_datetime = make_aware(datetime.combine(today, time.max))

        # Check if attendance exists for student
        if student:
            existing_attendance = Attendance.objects.filter(
                student=student,
                group=group,
                created_at__range=(start_datetime, end_datetime)
            ).exclude(id=instance_id).exists()

            if existing_attendance:
                raise serializers.ValidationError("This student has already been marked present today in this group.")

        # Check if attendance exists for lid
        if lid:
            existing_attendance = Attendance.objects.filter(
                lid=lid,
                group=group,
                created_at__range=(start_datetime, end_datetime)
            ).exclude(id=instance_id).exists()

            if existing_attendance:
                raise serializers.ValidationError("This lid has already been marked present today in this group.")

        return data

    def create(self, validated_data):
        from django.db import transaction

        # Extract themes from validated_data before creating the instance
        themes = validated_data.pop('theme', [])

        with transaction.atomic():
            attendance = Attendance.objects.create(**validated_data)

            if themes:
                attendance.theme.set(themes)
                attendance.save()

            student = validated_data.get('student')
            if student and themes:
                for theme in themes:
                    try:
                        homework = Homework.objects.filter(theme=theme).first()
                        if homework:
                            print(f"Creating homework history for theme: {theme}, student: {student}")
                            Homework_history.objects.create(
                                homework=homework,
                                student=student,
                                status="Passed",
                                mark=0
                            )
                            print(f"Homework history created successfully")
                            quiz = Quiz.objects.filter(homework=homework).first()

                            mastering = Mastering.objects.create(
                                student=student,
                                theme=homework.theme,
                                test=quiz,
                                ball=0
                            )

                            Mastering.objects.create(
                                student=student,
                                theme=theme,
                                test=None,
                                choice="Speaking",
                                ball=0
                            )
                        else:
                            print(f"No homework found for theme: {theme}")
                    except Exception as e:
                        print(f"Error creating homework history: {e}")

        return attendance

    @classmethod
    def create_bulk(cls, validated_data_list):
        """
        Handle bulk creation of attendance records
        """
        created_instances = []

        for data in validated_data_list:
            themes = data.pop('theme', [])

            # Create attendance instance
            attendance = Attendance.objects.create(**data)

            # Set themes
            if themes:
                attendance.theme.set(themes)

            # Create homework history
            student = data.get('student')
            if student and themes:
                for theme in themes:
                    try:
                        homework = Homework.objects.filter(theme=theme).first()
                        if homework:
                            Homework_history.objects.create(
                                homework=homework,
                                student=student,
                                status="Passed",
                                mark=0
                            )
                    except Exception as e:
                        print(f"Error creating homework history: {e}")

            created_instances.append(attendance)

        return created_instances

    def to_representation(self, instance):
        rep = super().to_representation(instance)

        rep['theme'] = ThemeSerializer(instance.theme, context=self.context, many=True).data
        if instance.lid:
            rep['lid'] = LidSerializer(instance.lid, context=self.context).data
        else:
            rep.pop('lid', None)

        if instance.student:
            rep['student'] = StudentSerializer(instance.student, context=self.context).data

        if instance.group:
            rep['group'] = instance.group.name

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

        rep['theme'] = ThemeSerializer(instance.theme, many=True, context=self.context).data
        filtered_data = {key: value for key, value in rep.items() if value not in [{}, [], None, "", False]}
        return filtered_data
