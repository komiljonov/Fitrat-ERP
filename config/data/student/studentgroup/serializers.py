from rest_framework import serializers

from .models import StudentGroup
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

        # Use try-except to avoid potential recursion or circular references
        try:
            # Limit the recursion depth by limiting which fields are serialized
            rep['group'] = GroupSerializer(instance.group, context=self.context).data
        except RecursionError:
            rep['group'] = "Error in serialization"

        if instance.lid:
            try:
                rep['lid'] = LidSerializer(instance.lid, context=self.context).data
            except RecursionError:
                rep['lid'] = "Error in serialization"
        else:
            rep.pop('lid', None)

        if instance.student:
            try:
                rep['student'] = StudentSerializer(instance.student, context=self.context).data
            except RecursionError:
                rep['student'] = "Error in serialization"
        else:
            rep.pop('student', None)

        # Filter out unwanted values
        filtered_data = {key: value for key, value in rep.items() if value not in [{}, [], None, "", False]}
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




