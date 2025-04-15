import hashlib
from datetime import datetime

from django.db.models import Avg, F
from rest_framework import serializers

from .models import Store
from ..attendance.models import Attendance
from ..groups.lesson_date_calculator import calculate_lessons
from ..mastering.models import Mastering
from ..student.models import Student
from ..studentgroup.models import StudentGroup, SecondaryStudentGroup
from ...account.serializers import UserSerializer
from ...department.filial.models import Filial
from ...department.filial.serializers import FilialSerializer
from ...department.marketing_channel.models import MarketingChannel
from ...department.marketing_channel.serializers import MarketingChannelSerializer
from ...finances.finance.models import Finance, VoucherStudent, SaleStudent
from ...parents.models import Relatives
from ...upload.models import File
from ...upload.serializers import FileUploadSerializer


class StoresSerializer(serializers.ModelSerializer):
    video = serializers.PrimaryKeyRelatedField(queryset=File.objects.all(), allow_null=True)

    class Meta:
        model = Store
        fields = [
            "id",
            "video",
            "seen",
            "created_at",
        ]

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["video"] = FileUploadSerializer(instance.video, context=self.context).data
        return rep


class StudentFinanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Finance
        fields = [
            "id",
            "casher",
            "student",
            "action",
            "amount",
            "kind",
            "payment_method",
            "creator",
            "comment",
            "created_at",
            "updated_at",
        ]


class StudentAPPSerializer(serializers.ModelSerializer):
    photo = serializers.PrimaryKeyRelatedField(queryset=File.objects.all(), allow_null=True)
    filial = serializers.PrimaryKeyRelatedField(queryset=Filial.objects.all(), allow_null=True)
    marketing_channel = serializers.PrimaryKeyRelatedField(queryset=MarketingChannel.objects.all(), allow_null=True)
    course = serializers.SerializerMethodField()
    group = serializers.SerializerMethodField()
    relatives = serializers.SerializerMethodField()
    file = serializers.PrimaryKeyRelatedField(queryset=File.objects.all(), many=True, allow_null=True)
    password = serializers.CharField(write_only=True, required=False, allow_null=True)
    attendance_count = serializers.SerializerMethodField()
    is_attendance = serializers.SerializerMethodField()
    secondary_group = serializers.SerializerMethodField()
    secondary_teacher = serializers.SerializerMethodField()
    learning = serializers.SerializerMethodField()
    teacher = serializers.SerializerMethodField()
    sales = serializers.SerializerMethodField()
    voucher = serializers.SerializerMethodField()

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
            "learning",
            'password',
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
            'balance_status',
            'balance',
            'service_manager',
            'course',
            'group',
            'teacher',
            'call_operator',
            'sales_manager',
            "is_archived",
            'is_frozen',
            "attendance_count",
            'relatives',
            'file',
            'secondary_group',
            'secondary_teacher',
            "new_student_stages",
            "new_student_date",
            "active_date",
            "created_at",
            "updated_at",
        ]

    def get_voucher(self, obj):
        voucher = VoucherStudent.objects.filter(student=obj)
        if voucher:
            return [{
                "id": voucher.voucher.id,
                "amount": voucher.voucher.amount,
                "is_expired": voucher.voucher.is_expired,
                "created_at": voucher.created_at,
            } for voucher in voucher]

    def get_sales(self, obj):
        sales = SaleStudent.objects.filter(student__id=obj.id)
        return [{
            "id": sale.sale.id,
            "amount": sale.sale.amount,
            "sale_status": sale.sale.status,
            "date": sale.expire_date.strftime('%Y-%m-%d')
            if sale.expire_date else "Unlimited"} for sale in sales]

    def get_teacher(self, obj):
        group = StudentGroup.objects.select_related('group__teacher').filter(student=obj).first()
        if group and group.group and group.group.teacher:
            teacher = group.group.teacher
            return {
                "id": teacher.id,
                "full_name": teacher.full_name
            }
        return None

    def get_learning(self, obj):
        mastering_qs = Mastering.objects.filter(student=obj)

        if not mastering_qs.exists():  # If no records, return default values
            return {
                "score": 1,  # Default lowest score
                "learning": 0  # Default lowest percentage
            }

        # Calculate the average score from 1 to 5
        average_score = mastering_qs.aggregate(avg_ball=Avg('ball'))['avg_ball'] or 0

        # Scale the score between 1 to 5 (assuming 0-100 scores exist)
        score_scaled = min(max(round(average_score / 20), 1), 5)  # Ensure it's between 1 to 5

        # Scale the percentage between 1 to 100
        percentage_scaled = min(max(round((average_score / 100) * 100), 0), 100)

        return {
            "score": score_scaled,
            "learning": percentage_scaled
        }

    def get_is_attendance(self, obj):
        groups = StudentGroup.objects.prefetch_related('group__scheduled_day_type').filter(student=obj)

        for group in groups:
            if not group.group:  # Ensure group.group is not None
                continue

            lesson_days_queryset = getattr(group.group, 'scheduled_day_type', None)
            if lesson_days_queryset is None:
                continue

            lesson_days = [day.name for day in lesson_days_queryset.all()] if hasattr(lesson_days_queryset,
                                                                                      'all') else []

            if not lesson_days:  # Skip iteration if no lesson days
                continue

            start_date = datetime.datetime.today()  # Keep it as a datetime object
            finish_date = start_date + datetime.timedelta(days=30)  # Properly add 30 days

            # Convert to string format for calculate_lessons
            start_date_str = start_date.strftime("%Y-%m-%d")
            finish_date_str = finish_date.strftime("%Y-%m-%d")

            dates = calculate_lessons(
                start_date=start_date_str,
                end_date=finish_date_str,
                lesson_type=','.join(lesson_days),
                holidays=[""],
                days_off=["Yakshanba"]
            )

            if not dates:
                continue

            first_month = min(dates.keys())  # Get the first available month
            lesson_date = dates[first_month][0]  # Get the first lesson date in that month

            attendance = Attendance.objects.filter(created_at__gte=lesson_date, student=obj).first()

            return {
                "date": lesson_date,
                "attendance": attendance.reason if attendance else "",
            }

        return {'is_attendance': None}  # Default return if no valid group found

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

    def get_course(self, obj):
        courses = (StudentGroup.objects.filter(student=obj)
                   .values("group__course__name", "group__course__level__name"))
        return list(courses)

    def get_group(self, obj):
        courses = (StudentGroup.objects.filter(student=obj)
        .values(
            "group__name", "group__status", "group__started_at", "group__ended_at", "group__teacher__first_name",
            "group__teacher__last_name"
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
        representation['photo'] = FileUploadSerializer(instance.photo, context=self.context).data
        representation['filial'] = FilialSerializer(instance.filial).data if instance.filial else None
        representation['marketing_channel'] = MarketingChannelSerializer(
            instance.marketing_channel).data if instance.marketing_channel else None

        representation['sales_manager'] = UserSerializer(
            instance.sales_manager).data if instance.sales_manager else None

        representation['service_manager'] = UserSerializer(
            instance.service_manager).data if instance.service_manager else None
        representation['file'] = FileUploadSerializer(instance.file.all(), many=True, context=self.context).data
        return representation


