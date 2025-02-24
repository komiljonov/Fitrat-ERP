import datetime
import hashlib

from django.db.models import F
from django.utils.module_loading import import_string
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import Student
from ..attendance.models import Attendance
from ..groups.lesson_date_calculator import calculate_lessons
from ..groups.models import SecondaryGroup, Group
from ..mastering.models import Mastering
from ..studentgroup.models import StudentGroup, SecondaryStudentGroup
from ...account.permission import PhoneAuthBackend
from ...account.serializers import UserSerializer
from ...department.filial.models import Filial
from ...department.filial.serializers import FilialSerializer
from ...department.marketing_channel.models import MarketingChannel
from ...department.marketing_channel.serializers import MarketingChannelSerializer
from ...parents.models import Relatives
from ...upload.models import File
from ...upload.serializers import FileUploadSerializer

class StudentSerializer(serializers.ModelSerializer):
    photo = serializers.PrimaryKeyRelatedField(queryset=File.objects.all(),allow_null=True)
    filial = serializers.PrimaryKeyRelatedField(queryset=Filial.objects.all(), allow_null=True)
    marketing_channel = serializers.PrimaryKeyRelatedField(queryset=MarketingChannel.objects.all(), allow_null=True)
    test = serializers.SerializerMethodField()
    course = serializers.SerializerMethodField()
    group = serializers.SerializerMethodField()
    relatives = serializers.SerializerMethodField()
    file = serializers.PrimaryKeyRelatedField(queryset=File.objects.all(), many=True,allow_null=True)
    # Use CharField for password
    password = serializers.CharField(write_only=True, required=False, allow_null=True)
    attendance_count = serializers.SerializerMethodField()

    is_attendance = serializers.SerializerMethodField()

    secondary_group = serializers.SerializerMethodField()
    secondary_teacher = serializers.SerializerMethodField()

    class Meta:
        model = Student
        fields = [
            'id',
            'photo',
            "first_name",
            "last_name",
            "middle_name",
            "is_attendance",
            "phone",
            'password',
            "date_of_birth",
            "education_lang",
            "student_type",
            "edu_class",
            "subject",
            "ball",
            "filial",
            "marketing_channel",
            "student_stage_type",
            'balance_status',
            'balance',
            "test",
            'service_manager',
            'course',
            'group',
            'call_operator',
            'sales_manager',
            "is_archived",
            'is_frozen',
            "attendance_count",
            'relatives',
            'file',
            'secondary_group',
            'secondary_teacher',
            "created_at",
            "updated_at",
        ]

    def get_is_attendance(self, obj):
        groups = StudentGroup.objects.filter(student=obj).values('group__id',"group__name")
        if groups:
            for group in groups:
                lesson_days_queryset = group.scheduled_day_type.all()  # This retrieves the related days
                lesson_days = [day.name for day in
                               lesson_days_queryset]
                start_date = datetime.datetime.today().strftime("%Y-%m-%d")
                end_date = group.finish_date.strftime("%Y-%m-%d") if obj.finish_date else None
                dates = calculate_lessons(
                    start_date=start_date,
                    end_date=end_date,
                    lesson_type=','.join(lesson_days),
                    holidays=[""],
                    days_off=["Yakshanba"]
                )
                lesson_date = dates[0]
                is_attendance = Attendance.objects.filter(created_at__gte=lesson_date,student=obj)
                if lesson_date == start_date and is_attendance.exists():
                    return {
                        'is_attendance': is_attendance.reason if is_attendance else lesson_date.strftime("%d-%m-%Y"),
                    }

    def get_secondary_group(self, obj):
        group = SecondaryStudentGroup.objects.filter(student=obj).annotate(
            name=F('group__name')  # Rename group__name to name
        ).values('id', 'name')

        # Convert the queryset to a list of dictionaries with keys as 'id' and 'name'
        group_list = [{'id': item['id'], 'name': item['name']} for item in group]
        return group_list[0] if group_list else None

    def get_secondary_teacher(self, obj):
        # Annotate the queryset to rename teacher's id, first_name, and last_name
        teacher = SecondaryStudentGroup.objects.filter(student=obj).annotate(
            teacher_id=F('group__teacher__id'),  # Rename to 'teacher_id'
            teacher_first_name=F('group__teacher__first_name'),  # Rename to 'teacher_first_name'
            teacher_last_name=F('group__teacher__last_name')  # Rename to 'teacher_last_name'
        ).values('teacher_id', 'teacher_first_name', 'teacher_last_name')

        # Convert the queryset to a list of dictionaries with custom keys
        teacher_list = [
            {'id': item['teacher_id'], 'first_name': item['teacher_first_name'], 'last_name': item['teacher_last_name']}
            for item in teacher]

        return teacher_list[0] if teacher_list else None

    def get_test(self, obj):
        test = Mastering.objects.filter(student=obj)
        MasteringSerializer = import_string("data.student.mastering.serializers.MasteringSerializer")
        return MasteringSerializer(test, many=True).data

    def get_course(self, obj):
        courses = (StudentGroup.objects.filter(student=obj)
                   .values("group__course__name", "group__course__level__name"))
        return list(courses)

    def get_group(self, obj):
        courses = (StudentGroup.objects.filter(student=obj)
                   .values(
                       "group__name", "group__status", "group__started_at", "group__ended_at", "group__teacher__first_name", "group__teacher__last_name"
                   ))
        return list(courses)

    def get_relatives(self, obj):
        relative = Relatives.objects.filter(student=obj).values('name', 'phone', 'who')
        return list(relative)

    def get_attendance_count(self, obj):
        attendance = Attendance.objects.filter(student=obj)
        return attendance.count() + 1

    def update(self, instance, validated_data):
        password = validated_data.get('password')
        if password:  # Only set the password if it's provided
            instance.password = hashlib.sha512(password.encode('utf-8')).hexdigest()
            instance.save()

        # Handle file updates with set()
        files = validated_data.get('file', None)
        if files is not None:
            # Convert the provided list of files to a set to avoid duplicates
            instance.file.set(files)

        # Update other fields
        for attr, value in validated_data.items():
            if attr != 'password' and attr != 'file':  # Skip the password and file fields
                setattr(instance, attr, value)

        instance.save()
        return instance

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['photo'] = FileUploadSerializer(instance.photo,context=self.context).data
        representation['filial'] = FilialSerializer(instance.filial).data if instance.filial else None
        representation['marketing_channel'] = MarketingChannelSerializer(
            instance.marketing_channel).data if instance.marketing_channel else None

        representation['sales_manager'] = UserSerializer(instance.sales_manager).data if instance.sales_manager else None

        representation['service_manager'] = UserSerializer(instance.service_manager).data if instance.service_manager else None
        representation['file'] = FileUploadSerializer(instance.file.all(), many=True, context=self.context).data
        return representation

class StudentTokenObtainPairSerializer(TokenObtainPairSerializer):
    phone = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        phone = attrs.get('phone')
        password = attrs.get('password')

        if phone and password:
            backend = PhoneAuthBackend()
            user = backend.authenticate(
                request=self.context.get('request'),
                phone=phone,
                password=password,
            )

            if not user:
                raise serializers.ValidationError(
                    "Unable to log in with provided credentials.",
                    code="authorization"
                )
        else:
            raise serializers.ValidationError(
                "Must include 'phone' and 'password'.",
                code="authorization"
            )

        attrs['user'] = user
        return attrs

class StudentAppSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = [
            'id',
            'first_name',
            'last_name',
        ]
    def get_attendance(self, obj):
        attendance = Attendance.objects.filter(lesson=obj)
        AttendanceSerializer = import_string(
            'data.student.attendance.serializers.AttendanceSerializer')
        return AttendanceSerializer(attendance, many=True).data
