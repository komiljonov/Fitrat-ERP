from datetime import date

from dateutil.relativedelta import relativedelta
from django.utils.module_loading import import_string
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import Student
from ..attendance.models import Attendance
from ..groups.lesson_date_calculator import calculate_lessons
from ..mastering.models import Mastering
from ..studentgroup.models import StudentGroup
from ...account.permission import PhoneAuthBackend
from ...account.serializers import UserSerializer
from ...department.filial.models import Filial
from ...department.filial.serializers import FilialSerializer
from ...department.marketing_channel.models import MarketingChannel
from ...department.marketing_channel.serializers import MarketingChannelSerializer
from ...parents.models import Relatives
from ...parents.serializers import RelativesSerializer


class StudentSerializer(serializers.ModelSerializer):
    filial = serializers.PrimaryKeyRelatedField(queryset=Filial.objects.all(),allow_null=True)
    marketing_channel = serializers.PrimaryKeyRelatedField(queryset=MarketingChannel.objects.all(),allow_null=True)
    test = serializers.SerializerMethodField()
    course = serializers.SerializerMethodField()
    group = serializers.SerializerMethodField()
    relatives = serializers.SerializerMethodField()

    password  = serializers.CharField(write_only=True,allow_null=True)
    attendance_count = serializers.SerializerMethodField()

    class Meta:
        model = Student
        fields = [
            'id',
            "first_name",
            "last_name",
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
            'moderator',
            'course',
            'group',
            'call_operator',

            'sales_manager',

            "is_archived",

            "attendance_count",

            'relatives',

            "created_at",
            "updated_at",
        ]


    def get_test(self, obj):
        test = Mastering.objects.filter(student=obj)
        MasteringSerializer = import_string("data.student.mastering.serializers.MasteringSerializer")
        return MasteringSerializer(test, many=True).data

    def get_course(self, obj):
        courses = (StudentGroup.objects.filter(student=obj)
                   .values("group__course__name","group__course__level__name"))
        return list(courses)

    def get_group(self, obj):
        courses = (StudentGroup.objects.filter(student=obj)
                   .values(
        "group__name", "group__status", "group__started_at", "group__ended_at","group__teacher__first_name","group__teacher__last_name"
        ))
        return list(courses)

    def get_relatives(self, obj):
        relative = Relatives.objects.filter(student=obj).values('name', 'phone', 'who')
        return list(relative)

    def get_attendance_count(self, obj):
        attendance = Attendance.objects.filter(student=obj)
        return attendance.count() + 1

    def update(self, instance, validated_data):
        if validated_data.get('password'):
            password = validated_data.get('password')
            instance.set_password(password)
            instance.save()

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['filial'] = FilialSerializer(instance.filial).data if instance.filial else None
        representation['marketing_channel'] = MarketingChannelSerializer(
            instance.marketing_channel).data if instance.marketing_channel else None

        representation['sales_manager'] = UserSerializer(instance.sales_manager).data if instance.sales_manager else None

        representation['moderator'] = UserSerializer(instance.moderator).data if instance.moderator else None

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
