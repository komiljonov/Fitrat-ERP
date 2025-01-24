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
    student = serializers.SerializerMethodField()
    lid = serializers.SerializerMethodField()

    class Meta:
        model = StudentGroup
        fields = [
            'id',
            'group',
            'lid',
            'student',
        ]

    def get_student(self, obj):
        """
        Fetch students related to this StudentGroup instance.
        """
        students = Student.objects.filter(studentgroup=obj)  # Use the related field
        return StudentSerializer(students, many=True).data

    def get_lid(self, obj):
        """
        Fetch lids related to this StudentGroup instance.
        """
        lids = Lid.objects.filter(studentgroup=obj)  # Use the related field
        return LidSerializer(lids, many=True).data

    def to_representation(self, instance):
        """
        Optionally combine students and lids into a single list.
        """
        representation = super().to_representation(instance)
        representation['combined'] = representation['student'] + representation['lid']
        return representation


