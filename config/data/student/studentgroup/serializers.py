from rest_framework import serializers

from rest_framework import serializers

from .models import StudentGroup, SecondaryStudentGroup
from ..groups.models import Group, SecondaryGroup
from ..groups.serializers import SecondaryGroupSerializer
from ..student.models import Student
from ..student.serializers import StudentSerializer
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

        if student:
            existing_student = StudentGroup.objects.filter(group=group, student=student).exists()
            if existing_student:
                raise serializers.ValidationError({"student": "Student in this group already exists"})

        if lid:
            existing_lid = StudentGroup.objects.filter(group=group, lid=lid).exists()
            if existing_lid:
                raise serializers.ValidationError({"lid": "Lid in this group already exists"})

        return attrs

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


from typing import List, Optional
class SecondaryStudentsGroupSerializer(serializers.ModelSerializer):
    group = serializers.PrimaryKeyRelatedField(queryset=SecondaryGroup.objects.all(), required=True)
    student = serializers.PrimaryKeyRelatedField(queryset=Student.objects.all(), allow_null=True)
    lid = serializers.PrimaryKeyRelatedField(queryset=Lid.objects.all(), allow_null=True)

    class Meta:
        model = SecondaryStudentGroup
        fields = ['id', 'group', 'lid', 'student']


    def to_representation(self, instance):
        rep = super().to_representation(instance)

        try:
            rep['group'] = SecondaryGroupSerializer(instance.group, context=self.context).data
        except RecursionError:
            rep['group'] = "Error in serialization"

        rep['lid'] = LidSerializer(instance.lid, context=self.context).data if instance.lid else None
        rep['student'] = StudentSerializer(instance.student, context=self.context).data if instance.student else None

        return {key: value for key, value in rep.items() if value not in [{}, [], None, "", False]}
