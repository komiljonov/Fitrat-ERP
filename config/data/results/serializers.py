from rest_framework import serializers

from data.account.models import CustomUser
from data.account.serializers import UserListSerializer
from data.results.models import Results
from data.student.student.models import Student
from data.student.student.serializers import StudentSerializer


class UniversityResultsSerializer(serializers.ModelSerializer):
    teacher = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())
    student = serializers.PrimaryKeyRelatedField(queryset=Student.objects.all())
    class Meta:
        model = Results
        fields = [
            'id',
            'results',
            'teacher',
            'student',
            'university_type',
            'university_name',
            'university_entering_type',
            'university_entering_ball',
            'created_at',
            'updated_at',
        ]

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["teacher"] = UserListSerializer(instance.teacher).data
        rep["student"] = StudentSerializer(instance.student).data
        return rep

class CertificationResultsSerializer(serializers.ModelSerializer):
    teacher = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())
    student = serializers.PrimaryKeyRelatedField(queryset=Student.objects.all())

    class Meta:
        model = Results
        fields = [
            'id',
            'results',
            'teacher',
            'student',
            'certificate_type',
            'band_score',
            'reading_score',
            'lessoning_score',
            'speaking_score',
            'writing_score',
            'created_at',
            'updated_at',
        ]

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["teacher"] = UserListSerializer(instance.teacher).data
        rep["student"] = StudentSerializer(instance.student).data
        return rep