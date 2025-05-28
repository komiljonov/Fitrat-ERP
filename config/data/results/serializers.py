from icecream import ic
from rest_framework import serializers

from data.account.models import CustomUser
from data.account.serializers import UserListSerializer
from data.finances.compensation.models import ResultName
from data.finances.compensation.serializers import ResultsNameSerializer
from data.results.models import Results
from data.student.student.models import Student
from data.student.student.serializers import StudentSerializer
from data.student.subject.models import Subject
from data.upload.models import File
from data.upload.serializers import FileUploadSerializer


class UniversityResultsSerializer(serializers.ModelSerializer):
    teacher = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())
    student = serializers.PrimaryKeyRelatedField(queryset=Student.objects.all())

    upload_file = serializers.PrimaryKeyRelatedField(queryset=File.objects.all(),many=True, allow_null=True)
    class Meta:
        model = Results
        fields = [
            'id',
            "who",
            'results',
            'teacher',
            'student',
            'university_type',
            'university_name',
            'university_entering_type',
            'university_entering_ball',
            'upload_file',
            'status',
            'created_at',
            'updated_at',
        ]

    def create(self, validated_data):
        upload_files = validated_data.pop('upload_file', [])

        result_instance = Results.objects.create(**validated_data)

        result_instance.upload_file.set(upload_files)

        return result_instance

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['upload_file'] = FileUploadSerializer(instance.upload_file, many=True,context=self.context).data if instance.upload_file else None
        rep["teacher"] = UserListSerializer(instance.teacher).data
        rep["student"] = StudentSerializer(instance.student).data
        return rep


class CertificationResultsSerializer(serializers.ModelSerializer):
    teacher = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())
    student = serializers.PrimaryKeyRelatedField(queryset=Student.objects.all())
    result_fk_name = serializers.PrimaryKeyRelatedField(queryset=ResultName.objects.all(), allow_null=True)
    upload_file = serializers.PrimaryKeyRelatedField(queryset=File.objects.all(), many=True, allow_null=True)
    class Meta:
        model = Results
        fields = [
            'id',
            "who",
            'results',
            "result_fk_name",
            'teacher',
            'student',
            'certificate_type',
            'band_score',
            'reading_score',
            'lessoning_score',
            'speaking_score',
            'writing_score',
            'upload_file',
            'status',
            'created_at',
            'updated_at',
        ]

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["result_fk_name"] = ResultsNameSerializer(instance.result_fk_name).data if instance.result_fk_name else None
        rep['upload_file'] = FileUploadSerializer(instance.upload_file, many=True,context=self.context).data if instance.upload_file else None
        rep["teacher"] = UserListSerializer(instance.teacher).data
        rep["student"] = StudentSerializer(instance.student).data
        return rep

    def create(self, validated_data):
        # Pop the 'upload_file' field to handle it separately
        upload_files = validated_data.pop('upload_file', [])

        # Create the Results instance
        certificate = Results.objects.create(**validated_data)

        # If 'upload_file' has data, assign the file instances to the Results instance
        if upload_files:
            certificate.upload_file.set(upload_files)

        return certificate

class StudentResultsSerializer(serializers.ModelSerializer):
    teacher = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())
    student = serializers.PrimaryKeyRelatedField(queryset=Student.objects.all())
    upload_file = serializers.PrimaryKeyRelatedField(queryset=File.objects.all(), many=True, allow_null=True)

    national = serializers.PrimaryKeyRelatedField(queryset=Subject.objects.all(),allow_null=True)

    result_fk_name = serializers.PrimaryKeyRelatedField(queryset=ResultName.objects.all(),allow_null=True)


    class Meta:
        model = Results
        fields = [
            'id',
            "who",
            'results',
            'teacher',
            'student',
            "result_fk_name",
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

            'national',

            'result_name',
            'result_score',
            'subject_name',

            'upload_file',
            'status',

            "updater",

            'created_at',
            'updated_at',
        ]

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['upload_file'] = FileUploadSerializer(instance.upload_file, many=True,context=self.context).data if instance.upload_file else None
        rep["teacher"] = UserListSerializer(instance.teacher).data
        rep["student"] = StudentSerializer(instance.student, context=self.context).data
        return rep

    def create(self, validated_data):
        # Pop the 'upload_file' field to handle it separately
        upload_files = validated_data.pop('upload_file', [])

        # Create the Results instance
        certificate = Results.objects.create(**validated_data)

        # If 'upload_file' has data, assign the file instances to the Results instance
        if upload_files:
            certificate.upload_file.set(upload_files)

        return certificate

    def update(self, instance, validated_data):

        request = self.context.get("request")

        if validated_data["status"]:
            instance.updater = request.user
            instance.save()


class OtherResultsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Results
        fields = [
            'id',
            "who",
            'teacher',
            'student',
            'certificate_type',
            'result_name',
            'result_score',
            'subject_name',
            'status',
            'upload_file',
            'created_at',
            'updated_at',
        ]

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['upload_file'] = FileUploadSerializer(instance.upload_file, many=True,
                                                  context=self.context).data if instance.upload_file else None
        rep["teacher"] = UserListSerializer(instance.teacher).data
        rep["student"] = StudentSerializer(instance.student).data
        return rep

    def create(self, validated_data):
        # Pop the 'upload_file' field to handle it separately
        upload_files = validated_data.pop('upload_file', [])

        # Create the Results instance
        certificate = Results.objects.create(**validated_data)

        # If 'upload_file' has data, assign the file instances to the Results instance
        if upload_files:
            certificate.upload_file.set(upload_files)

        return certificate

class NationalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Results
        fields = [
            'id',
            "who",
            'results',
            'teacher',
            'student',
            'certificate_type',
            'national',
            'band_score',
            'upload_file',
            'status',
        ]

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['upload_file'] = FileUploadSerializer(instance.upload_file, many=True,
                    context=self.context).data if instance.upload_file else None
        rep["teacher"] = UserListSerializer(instance.teacher).data
        rep["student"] = StudentSerializer(instance.student).data
        return rep

    def create(self, validated_data):
        # Pop the 'upload_file' field to handle it separately
        upload_files = validated_data.pop('upload_file', [])

        # Create the Results instance
        certificate = Results.objects.create(**validated_data)

        # If 'upload_file' has data, assign the file instances to the Results instance
        if upload_files:
            certificate.upload_file.set(upload_files)

        return certificate


class ResultsSerializer(serializers.ModelSerializer):
    student = serializers.PrimaryKeyRelatedField(queryset=Student.objects.all())
    class Meta:
        model = Results
        fields = [
            'id',
            "who",
            'results',
            'teacher',
            'student',
            "national",
            'university_type',
            'university_name',
            'university_entering_type',
            'university_entering_ball',
            'certificate_type',
            'band_score',
            'reading_score',
            'lessoning_score',
            'speaking_score',
            'writing_score',
            'result_name',
            'result_score',
            'subject_name',
            'upload_file',
            'status',
            "updater",
            'created_at',
            'updated_at',
        ]

    def update(self, instance, validated_data):
        request = self.context.get("request")

        # Set updater for any update
        if request and request.user:
            validated_data['updater'] = request.user

        # Call the parent update method to handle all field updates
        return super().update(instance, validated_data)

    def to_representation(self, instance):

        """ Remove fields that are None or empty """

        data = super().to_representation(instance)
        data["updater"] = UserListSerializer(instance.updater).data if instance.updater else None
        data['upload_file'] = FileUploadSerializer(instance.upload_file,context=self.context, many=True,).data
        data['student'] = StudentSerializer(instance.student,context=self.context).data
        data['teacher'] = UserListSerializer(instance.teacher,context=self.context).data
        return {key: value for key, value in data.items() if value not in [None, "", []]}
