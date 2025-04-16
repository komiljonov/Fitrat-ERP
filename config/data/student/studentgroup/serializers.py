from rest_framework import serializers

from .models import StudentGroup, SecondaryStudentGroup
from ..groups.models import Group, SecondaryGroup
from ..groups.serializers import SecondaryGroupSerializer
from ..student.models import Student
from ..student.serializers import StudentSerializer
from ...account.models import CustomUser
from ...lid.new_lid.models import Lid
from ...lid.new_lid.serializers import LidSerializer


class StudentsGroupSerializer(serializers.ModelSerializer):
    group = serializers.PrimaryKeyRelatedField(queryset=Group.objects.all())
    student = serializers.PrimaryKeyRelatedField(queryset=Student.objects.all(),allow_null=True)
    lid = serializers.PrimaryKeyRelatedField(queryset=Lid.objects.all(),allow_null=True)


    class Meta:
        model = StudentGroup
        fields = [
            'id',
            'group',
            'lid',
            'student',
        ]

    def validate(self, attrs):
        student = attrs.get("student")
        lid = attrs.get("lid")
        group = attrs.get("group")

        if student and group:
            # Ensure that a student is not added to the same group twice
            existing_student = StudentGroup.objects.filter(group=group, student=student).exclude(
                id=self.instance.id if self.instance else None).exists()
            if existing_student:
                raise serializers.ValidationError({"student": "O'quvchi ushbu guruhda allaqachon mavjud!"})

        if lid and group:
            # Ensure that a lid is not added to the same group twice
            existing_lid = StudentGroup.objects.filter(group=group, lid=lid).exclude(
                id=self.instance.id if self.instance else None).exists()
            if existing_lid:
                raise serializers.ValidationError({"lid": "Lid ushbu guruhda allaqachon mavjud!"})

        return attrs

    def create(self, validated_data):
        filial = validated_data.pop("filial", None)
        if not filial:
            request = self.context.get("request")  #
            if request and hasattr(request.user, "filial"):
                filial = request.user.filial.first()

        if not filial:
            raise serializers.ValidationError({"filial": "Filial could not be determined."})

        room = StudentGroup.objects.create(filial=filial, **validated_data)
        return room

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        if instance.group:
            group_data = {
                'group_name': instance.group.name,
                'course': instance.group.course.name,
                'teacher': instance.group.teacher.full_name if instance.group.teacher else None,
                'room_number': instance.group.room_number.room_number,
                'course_id': instance.group.course.id,
            }
            rep['group'] = group_data

        else:
            rep.pop('group', None)

        if instance.lid:
            rep['lid'] = LidSerializer(instance.lid).data

        else:
            rep.pop('lid', None)

        if instance.student:
            rep['student'] = StudentSerializer(instance.student).data

        else:
            rep.pop('student', None)



        # Filter out unwanted values
        filtered_data = {key: value for key, value in rep.items() if value not in [{}, None, "", False]}
        return filtered_data


class StudentGroupMixSerializer(serializers.ModelSerializer):
    # group = serializers.PrimaryKeyRelatedField(queryset=Group.objects.all())
    student = serializers.PrimaryKeyRelatedField(queryset=Student.objects.all())
    lid = serializers.PrimaryKeyRelatedField(queryset=Lid.objects.all())

    class Meta:
        model = StudentGroup
        fields = [
            'id',
            'group',
            'student',
            'lid',
        ]

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        # rep['group'] = GroupSerializer(instance.group).data
        rep['student'] = StudentSerializer(instance.student).data
        rep['lid'] = LidSerializer(instance.lid).data
        return rep


class SecondaryStudentsGroupSerializer(serializers.ModelSerializer):
    group = serializers.PrimaryKeyRelatedField(queryset=SecondaryGroup.objects.all(), required=True)
    student = serializers.PrimaryKeyRelatedField(queryset=Student.objects.all(), allow_null=True)
    lid = serializers.PrimaryKeyRelatedField(queryset=Lid.objects.all(), allow_null=True)
    main_teacher = serializers.SerializerMethodField()

    class Meta:
        model = SecondaryStudentGroup
        fields = ['id', 'group', 'lid',"main_teacher" ,'student']


    def create(self, validated_data):
        filial = validated_data.pop("filial", None)
        if not filial:
            request = self.context.get("request")  #
            if request and hasattr(request.user, "filial"):
                filial = request.user.filial.first()

        if not filial:
            raise serializers.ValidationError({"filial": "Filial could not be determined."})

        room = SecondaryStudentGroup.objects.create(filial=filial, **validated_data)
        return room

    def get_main_teacher(self, instance):
        try:
            return SecondaryGroup.objects.get(id=instance.group.id).teacher
        except SecondaryGroup.DoesNotExist:
            return None
    def validate_group(self, value):
        if not SecondaryGroup.objects.filter(id=value.id).exists():
            raise serializers.ValidationError("Invalid group ID")
        return value

    def validate_student(self, value):
        if not Student.objects.filter(id=value.id).exists():
            raise serializers.ValidationError("Invalid student ID")
        return value

    def validate_lid(self, value):
        if value and not Lid.objects.filter(id=value.id).exists():
            raise serializers.ValidationError("Invalid lid ID")
        return value

    def to_representation(self, instance):
        rep = super().to_representation(instance)

        rep['group'] = SecondaryGroupSerializer(instance.group, context=self.context).data
        rep['lid'] = LidSerializer(instance.lid, context=self.context).data if instance.lid else None
        rep['student'] = StudentSerializer(instance.student, context=self.context).data if instance.student else None

        return {key: value for key, value in rep.items() if value not in [{}, [], None, "", False]}
