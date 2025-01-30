from rest_framework import serializers

from data.account.models import CustomUser
from data.account.serializers import UserListSerializer
from data.results.models import Results
from data.student.student.models import Student
from data.student.student.serializers import StudentSerializer
from data.upload.models import File
from data.upload.serializers import FileUploadSerializer


class UniversityResultsSerializer(serializers.ModelSerializer):
    teacher = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())
    student = serializers.PrimaryKeyRelatedField(queryset=Student.objects.all())

    upload_file = serializers.PrimaryKeyRelatedField(queryset=File.objects.all())
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
            'upload_file',
            'created_at',
            'updated_at',
        ]

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['upload_file'] = FileUploadSerializer(instance.file).data
        rep["teacher"] = UserListSerializer(instance.teacher).data
        rep["student"] = StudentSerializer(instance.student).data
        return rep

class CertificationResultsSerializer(serializers.ModelSerializer):
    teacher = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())
    student = serializers.PrimaryKeyRelatedField(queryset=Student.objects.all())
    upload_file = serializers.PrimaryKeyRelatedField(queryset=File.objects.all())
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
            'upload_file',
            'created_at',
            'updated_at',
        ]

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['upload_file'] = FileUploadSerializer(instance.file).data
        rep["teacher"] = UserListSerializer(instance.teacher).data
        rep["student"] = StudentSerializer(instance.student).data
        return rep

class StudentResultsSerializer(serializers.ModelSerializer):
    teacher = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())
    student = serializers.PrimaryKeyRelatedField(queryset=Student.objects.all())
    upload_file = serializers.PrimaryKeyRelatedField(queryset=File.objects.all())

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
            'university_type',
            'university_name',
            'university_entering_type',
            'university_entering_ball',
            'upload_file',
            'created_at',
            'updated_at',
        ]

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['upload_file'] = FileUploadSerializer(instance.upload_file).data
        rep["teacher"] = UserListSerializer(instance.teacher).data
        rep["student"] = StudentSerializer(instance.student).data
        return rep