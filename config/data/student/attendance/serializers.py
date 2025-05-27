from datetime import datetime, time

from django.utils.timezone import now, make_aware
from icecream import ic
from rest_framework import serializers

from .models import Attendance
from ..homeworks.models import Homework, Homework_history
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
        # Handle bulk creation manually
        if isinstance(validated_data, list):
            instances = []
            mastering_to_create = []

            for item in validated_data:
                # Create the attendance instance
                instance = Attendance.objects.create(**item)
                instances.append(instance)

                # Collect mastering creation data for each instance
                if instance.student and instance.theme:
                    try:
                        # Get homework related to the theme
                        homework = Homework.objects.filter(theme=instance.theme).first()

                        if homework:
                            # Check if homework history exists with mark=0
                            homework_history = Homework_history.objects.filter(
                                homework=homework,
                                group=instance.group,
                                student=instance.student,
                                mark=0
                            ).first()

                            if homework_history:
                                # Collect mastering data for bulk creation
                                mastering_data = {
                                    'student': instance.student,
                                    'theme': instance.theme,
                                    'group': instance.group,
                                    'homework': homework,
                                    # Add other fields as needed
                                }
                                mastering_to_create.append(mastering_data)

                    except Exception as e:
                        # Log the error but don't fail the attendance creation
                        print(f"Error preparing mastering for attendance {instance.id}: {e}")

            # Bulk create mastering records if any
            if mastering_to_create:
                try:
                    # Replace 'Mastering' with your actual model name
                    # Mastering.objects.bulk_create([
                    #     Mastering(**data) for data in mastering_to_create
                    # ], ignore_conflicts=True)  # ignore_conflicts prevents duplicates
                    pass  # Replace with your actual bulk creation
                except Exception as e:
                    print(f"Error bulk creating mastering records: {e}")

            return instances

        # Handle single instance creation
        instance = super().create(validated_data)

        # Handle mastering creation for single instance
        if instance.student and instance.theme:
            try:
                homework = Homework.objects.filter(theme=instance.theme).first()

                if homework:
                    homework_history = Homework_history.objects.filter(
                        homework=homework,
                        group=instance.group,
                        student=instance.student,
                        mark=0
                    ).first()

                    if homework_history:
                        # Add your mastering creation logic here
                        pass

            except Exception as e:
                print(f"Error creating mastering for attendance {instance.id}: {e}")

        return instance

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

        rep['theme'] = ThemeSerializer(instance.theme, many=True, context=self.context).data
        filtered_data = {key: value for key, value in rep.items() if value not in [{}, [], None, "", False]}
        return filtered_data
