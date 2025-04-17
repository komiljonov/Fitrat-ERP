from django.db.models import Q
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import Lid
from ...account.models import CustomUser
from ...account.serializers import UserSerializer
from ...department.filial.models import Filial
from ...department.filial.serializers import FilialSerializer
from ...department.marketing_channel.models import MarketingChannel
from ...department.marketing_channel.serializers import MarketingChannelSerializer
from ...finances.finance.models import SaleStudent, Voucher, VoucherStudent
from ...parents.models import Relatives
from ...student.attendance.models import Attendance
from ...student.lesson.models import FirstLLesson
from ...student.student.models import Student
from ...student.studentgroup.models import StudentGroup
from ...upload.models import File
from ...upload.serializers import FileUploadSerializer
from ...upload.views import UploadFileAPIView


class LidSerializer(serializers.ModelSerializer):
    photo = serializers.PrimaryKeyRelatedField(queryset=File.objects.all(),allow_null=True)
    filial = serializers.PrimaryKeyRelatedField(queryset=Filial.objects.all(), allow_null=True)
    marketing_channel = serializers.PrimaryKeyRelatedField(queryset=MarketingChannel.objects.all(), allow_null=True)
    call_operator = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all(),
                                                       allow_null=True)
    service_manager = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all(), allow_null=True)
    sales_manager = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all(), allow_null=True)

    course = serializers.SerializerMethodField()
    group = serializers.SerializerMethodField()
    lessons_count = serializers.SerializerMethodField()
    relatives = serializers.SerializerMethodField()
    file = serializers.PrimaryKeyRelatedField(queryset=File.objects.all(), many=True, allow_null=True)
    is_attendance = serializers.SerializerMethodField()
    student = serializers.PrimaryKeyRelatedField(queryset=Student.objects.all(), allow_null=True)
    sales = serializers.SerializerMethodField()
    voucher = serializers.SerializerMethodField()

    class Meta:
        model = Lid
        fields = [
            "id", "sender_id", "message_text", "photo" ,"first_name", "last_name", "middle_name",
            "phone_number", "date_of_birth", "education_lang", "student_type","sales","voucher","ordered_date",
            "edu_class", "edu_level", "subject", "ball", "filial","is_frozen","is_attendance",
            "marketing_channel", "lid_stage_type", "ordered_stages","extra_number","student","balance",
            "lid_stages", "is_archived", "course", "group", "service_manager",'is_student',
            "call_operator", "relatives", "lessons_count", "created_at","sales_manager","is_expired","file"
        ]

    def __init__(self, *args, **kwargs):
        fields_to_remove: list | None = kwargs.pop("remove_fields", None)
        super(LidSerializer, self).__init__(*args, **kwargs)

        if fields_to_remove:
            for field in fields_to_remove:
                self.fields.pop(field, None)

    def get_voucher(self, obj):
        voucher = VoucherStudent.objects.filter(lid__id=obj.id)
        return [{
                "id":voucher.voucher.id,
                "amount":voucher.voucher.amount,
                "is_expired":voucher.voucher.is_expired,
                "created_at": voucher.created_at,
            } for voucher in voucher]

    def get_sales(self, obj):
        sales = SaleStudent.objects.filter(lid__id=obj.id)
        return [{
            "id": sale.sale.id,
            "amount": sale.sale.amount,
            "sale_status":sale.sale.status ,
            "date": sale.expire_date.strftime('%Y-%m-%d')
        if sale.expire_date else "Unlimited"} for sale in sales]

    def get_filtered_queryset(self):
        request = self.context.get('request')
        if not request:
            return Lid.objects.none()

        user = request.user
        queryset = Lid.objects.all()

        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        if start_date:
            queryset = queryset.filter(created_at__gte=start_date)
        if end_date:
            queryset = queryset.filter(created_at__lte=end_date)

        if user.role == 'CALL_OPERATOR':
            queryset = queryset.filter(Q(call_operator=user) | Q(call_operator=None), filial=None)
        return queryset

    def get_is_attendance(self, obj):
        first_lesson = FirstLLesson.objects.filter(lid=obj).first()
        if first_lesson :
            return {
                "date": first_lesson.date,
                "time": first_lesson.time,
            }

    def get_lessons_count(self, obj):
        return Attendance.objects.filter(lid=obj, reason="IS_PRESENT").count()

    def get_relatives(self, obj):
        relative = (Relatives.objects.filter(lid=obj)
                    .values('name','phone','who'))
        return list(relative)

    def get_course(self, obj):
        return StudentGroup.objects.filter(lid=obj).values_list("group__course__name","group__course__level__id")

    def get_group(self, obj):
        return list(StudentGroup.objects.filter(lid=obj).values_list("group__id","group__teacher__id","group__name"))

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['photo'] = FileUploadSerializer(instance.photo,context=self.context).data
        representation['filial'] = FilialSerializer(instance.filial).data if instance.filial else None
        representation['marketing_channel'] = MarketingChannelSerializer(
            instance.marketing_channel).data if instance.marketing_channel else None
        representation['call_operator'] = UserSerializer(
            instance.call_operator).data if instance.call_operator else None
        representation['file'] = FileUploadSerializer(instance.file.all(), many=True,context=self.context).data
        return representation

    def update(self, instance, validated_data):
        request = self.context['request']

        # Ensure call_operator is updated properly
        if instance.lid_stage_type == "NEW_LID" and request.user.role == 'CALL_OPERATOR' or request.user.is_call_center == True:
            instance.call_operator = request.user

        if instance.lid_stage_type == "ORDERED_LID" and request.user.role == 'ADMINISTRATOR':
            # instance.
            instance.sales_manager = request.user
            instance.filial = request.user.filial.first()

        # Update call_operator from request if provided
        if "call_operator" in validated_data:
            instance.call_operator = validated_data["call_operator"]

        # Handling file updates using set()
        files = validated_data.get('file', None)
        if files is not None:
            instance.file.set(files)  # Use set() to assign files

        # Update other fields
        for attr, value in validated_data.items():
            if attr not in ["file", "call_operator"]:  # Skip file field to avoid conflict
                setattr(instance, attr, value)

        instance.save()

        return instance

    def create(self, validated_data):
        request = self.context['request']

        if request.user.role == 'CALL_OPERATOR':
            validated_data['call_operator'] = request.user
            if request.user.filial is not None:
                validated_data['filial'] = request.user.filial.first()

        elif request.user.role == 'ADMINISTRATOR' and request.user.filial is not None:
            validated_data['sales_manager'] = request.user
            validated_data['filial'] = request.user.filial.first()

        else:
            validated_data['filial'] = request.user.filial.first()

        # Handle file field using set() to avoid Many-to-Many direct assignment error
        files = validated_data.pop('file', None)  # Remove the file field from validated_data
        instance = Lid.objects.create(**validated_data)  # Create the instance first

        # Now assign files to the ManyToMany relationship using set()
        if files is not None:
            instance.file.set(files)

        return instance

class LidStatisticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lid
        fields = [
            "id","first_name", "last_name", "middle_name",
            "phone_number",  "education_lang", "student_type", "subject","filial",
            "marketing_channel", "lid_stage_type", "ordered_stages",
            "lid_stages", "is_archived", "course", "group", "service_manager",'is_student',
            "call_operator", "created_at","sales_manager",
        ]

class LidAppSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lid
        fields = [
            'id',
            'first_name',
            'last_name',
        ]

class LidBulkUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lid
        fields = [
            'id', 'sender_id', 'message_text', 'first_name', 'last_name', 'middle_name', 'phone_number',
            'date_of_birth', 'education_lang', 'student_type', 'edu_class', 'edu_level', 'subject',
            'ball', 'filial', 'marketing_channel', 'lid_stage_type', 'lid_stages', 'ordered_stages',
            'is_archived', 'is_dubl', 'call_operator', 'is_student', 'service_manager', 'sales_manager'
        ]

    def update_bulk_lids(self, lids_data):
        lids_to_update = []
        for lid_data in lids_data:
            lid_id = lid_data.get('id')
            try:
                lid_instance = Lid.objects.get(id=lid_id)
                # Validate and update fields
                lid_instance = self.update(lid_instance, lid_data)  # This uses the `update` method from ModelSerializer
                lids_to_update.append(lid_instance)
            except Lid.DoesNotExist:
                raise ValidationError(f"Lid with ID {lid_id} does not exist.")

        # Perform bulk update using Django's bulk_update method
        if lids_to_update:
            Lid.objects.bulk_update(lids_to_update, [
                'sender_id', 'message_text', 'first_name', 'last_name', 'middle_name', 'phone_number',
                'date_of_birth', 'education_lang', 'student_type', 'edu_class', 'edu_level', 'subject',
                'ball', 'filial', 'marketing_channel', 'lid_stage_type', 'lid_stages', 'ordered_stages',
                'is_archived', 'is_dubl', 'call_operator', 'is_student', 'service_manager', 'sales_manager'
            ])
        return lids_to_update