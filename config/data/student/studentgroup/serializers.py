import datetime
from datetime import date

import icecream
from rest_framework import serializers

from .models import StudentGroup, SecondaryStudentGroup
from ..attendance.models import Attendance
from ..groups.models import Group
from ..groups.serializers import GroupSerializer
from ..student.models import Student
from ..student.serializers import StudentSerializer
from ...lid.new_lid.models import Lid
from ...lid.new_lid.serializers import LidSerializer


class StudentsGroupSerializer(serializers.ModelSerializer):
    group = serializers.PrimaryKeyRelatedField(queryset=Group.objects.all())
    student = serializers.PrimaryKeyRelatedField(queryset=Student.objects.all())
    lid = serializers.PrimaryKeyRelatedField(queryset=Lid.objects.all())


    class Meta:
        model = StudentGroup
        fields = [
            'id',
            'group',
            'lid',
            'student',
        ]


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
    group = serializers.PrimaryKeyRelatedField(queryset=Group.objects.all())
    student = serializers.PrimaryKeyRelatedField(queryset=Student.objects.all())
    lid = serializers.PrimaryKeyRelatedField(queryset=Lid.objects.all())

    class Meta:
        model = SecondaryStudentGroup
        fields = [
            'id',
            'group',
            'lid',
            'student',
        ]

    def __init__(self, *args, **kwargs):
        # Call the parent constructor

        # Fields you want to remove (for example, based on some condition)
        fields_to_remove: list | None = kwargs.pop("remove_fields", None)
        super(SecondaryStudentsGroupSerializer, self).__init__(*args, **kwargs)

        if fields_to_remove:
            # Remove the fields from the serializer
            for field in fields_to_remove:
                self.fields.pop(field, None)

    def to_representation(self, instance):
        rep = super().to_representation(instance)

        # Use try-except to avoid potential recursion or circular references
        try:
            # Limit the recursion depth by limiting which fields are serialized
            rep['group'] = GroupSerializer(instance.group, context=self.context).data
        except RecursionError:
            rep['group'] = "Error in serialization"

        if instance.lid:
            rep['lid'] = LidSerializer(instance.lid, context=self.context, remove_fields=["student_group"]).data

        else:
            rep.pop('lid', None)

        if instance.student:
            rep['student'] = StudentSerializer(instance.student, context=self.context,remove_fields=["student_group"]).data

        else:
            rep.pop('student', None)

        # Filter out unwanted values
        filtered_data = {key: value for key, value in rep.items() if value not in [{}, [], None, "", False]}
        return filtered_data