from icecream import ic
from rest_framework import serializers

from data.account.models import CustomUser
from data.account.serializers import UserListSerializer
from data.finances.compensation.models import ResultName, ResultSubjects
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

    def validate(self, attrs):
        # Call parent validation first
        attrs = super().validate(attrs)

        # Get values from instance (update) or attrs (creation)
        if self.instance:
            # Update scenario
            university_entering_type = self.instance.university_entering_type
            university_type = self.instance.university_type
        else:
            # Creation scenario
            university_entering_type = attrs.get('university_entering_type')
            university_type = attrs.get('university_type')

        # Only validate if we have the required fields
        if university_entering_type and university_type:
            entry = "Grant" if university_entering_type == "Grant" else "Contract"
            mapped_university_type = "Personal" if university_type == "Unofficial" else "National"

            level = ResultSubjects.objects.filter(
                asos__name__icontains="ASOS_4",
                entry_type=entry,
                university_type=mapped_university_type,
            ).first()

            if not level:
                raise serializers.ValidationError("Ushbu amalni tasdiqlash uchun monitoring yaratilmagan!")

        return attrs

    def create(self, validated_data):
        upload_files = validated_data.pop('upload_file', [])

        certificate = Results.objects.create(**validated_data)

        if upload_files:
            certificate.upload_file.set(upload_files)

        return certificate

    def update(self, instance, validated_data):
        request = self.context.get("request")

        upload_files = validated_data.pop('upload_file', None)

        if validated_data.get("status"):
            validated_data['updater'] = request.user

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        if upload_files is not None:
            if upload_files:
                instance.upload_file.set(upload_files)
            else:
                instance.upload_file.clear()

        return instance

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['upload_file'] = FileUploadSerializer(instance.upload_file, many=True,context=self.context).data if instance.upload_file else None
        rep["teacher"] = UserListSerializer(instance.teacher).data
        rep["student"] = StudentSerializer(instance.student).data
        return rep


class CertificationResultsSerializer(serializers.ModelSerializer):
    teacher = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())
    student = serializers.PrimaryKeyRelatedField(queryset=Student.objects.all(), allow_null=True)
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
            # 'certificate_type',
            'band_score',
            'reading_score',
            'listening_score',
            'speaking_score',
            'writing_score',
            'upload_file',
            'status',
            'created_at',
            'updated_at',
        ]

    def validate(self, attrs):
        """Main validation method"""
        # Call parent validation first
        attrs = super().validate(attrs)


        if not (self.instance and self.instance.result_fk_name and
                self.instance.point and self.instance.who):
            return attrs

        try:
            result_name = ResultName.objects.filter(
                id=self.instance.result_fk_name.id,
                who=self.instance.who,
            ).first()

            if not result_name:
                raise serializers.ValidationError(
                    "Ushbu amalni tasdiqlash uchun monitoring yaratilmagan!"
                )

            # Get subject based on point type
            point_type = self.instance.point.point_type
            band_score = self.instance.band_score
            subject = None

            base_query = ResultSubjects.objects.filter(
                asos__name__icontains="ASOS_4",
                result=self.instance.point,
                result_type=self.instance.who,
            )

            if point_type in ["Percentage", "Ball"] and band_score is not None:
                subject = base_query.filter(from_point=band_score).first()

            elif point_type == "Degree" and band_score:
                subject = base_query.filter(from_point__icontains=band_score).first()

            if not subject:
                raise serializers.ValidationError(
                    "Ushbu amalni tasdiqlash uchun monitoring yaratilmagan!"
                )

        except (AttributeError, ValueError, TypeError):
            raise serializers.ValidationError(
                "Ushbu amalni tasdiqlash uchun monitoring yaratilmagan!"
            )

        return attrs

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["result_fk_name"] = ResultsNameSerializer(instance.result_fk_name).data if instance.result_fk_name else None
        rep['upload_file'] = FileUploadSerializer(instance.upload_file, many=True,context=self.context).data if instance.upload_file else None
        rep["teacher"] = UserListSerializer(instance.teacher).data
        rep["student"] = StudentSerializer(instance.student).data if instance.student else None
        return rep

    def create(self, validated_data):
        upload_files = validated_data.pop('upload_file', [])

        certificate = Results.objects.create(**validated_data)

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
#             'certificate_type',
            'band_score',
            'reading_score',
            'listening_score',
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
        rep["result_fk_name"] = ResultsNameSerializer(instance.result_fk_name).data if instance.result_fk_name else None
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

        upload_files = validated_data.pop('upload_file', None)

        if validated_data.get("status"):
            validated_data['updater'] = request.user

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        if upload_files is not None:
            if upload_files:
                instance.upload_file.set(upload_files)
            else:
                instance.upload_file.clear()

        return instance


class OtherResultsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Results
        fields = [
            'id',
            "who",
            "results",
            'teacher',
            'student',
#             'certificate_type',
            "level",
            'result_name',
            'result_score',
            'subject_name',
            'status',
            "degree",
            'upload_file',
            'created_at',
            'updated_at',
        ]

    def validate(self, attrs):
        # Call parent validation first
        attrs = super().validate(attrs)

        if self.instance:
            query = ResultSubjects.objects.filter(
                asos__name__icontains="ASOS_4",
                level=attrs["level"],
                degree=attrs["degree"],
            ).first()
            if not query:
                raise serializers.ValidationError(
                    "Ushbu amalni tasdiqlash uchun monitoring yaratilmagan!"
                )
        return attrs

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['upload_file'] = FileUploadSerializer(
            instance.upload_file, many=True,context=self.context).data \
            if instance.upload_file else None
        rep["teacher"] = UserListSerializer(instance.teacher).data
        rep["student"] = StudentSerializer(instance.student).data
        return rep

    def create(self, validated_data):
        upload_files = validated_data.pop('upload_file', [])

        certificate = Results.objects.create(**validated_data)

        if upload_files:
            certificate.upload_file.set(upload_files)

        return certificate

    def update(self, instance, validated_data):
        request = self.context.get("request")

        upload_files = validated_data.pop('upload_file', None)

        if validated_data.get("status"):
            validated_data['updater'] = request.user

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        if upload_files is not None:
            if upload_files:
                instance.upload_file.set(upload_files)
            else:
                instance.upload_file.clear()

        return instance


class NationalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Results
        fields = [
            'id',
            "who",
            'results',
            'teacher',
            'student',
#             'certificate_type',
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
            "level",
            'student',
            "national",
            'university_type',
            'university_name',
            'university_entering_type',
            'university_entering_ball',
#             'certificate_type',
            "degree",
            'band_score',
            'reading_score',
            'listening_score',
            'speaking_score',
            'writing_score',
            'result_name',
            'result_score',
            'subject_name',
            'upload_file',
            'status',
            "updater",
            "result_fk_name",
            'created_at',
            'updated_at',
        ]

    def update(self, instance, validated_data):
        request = self.context.get("request")

        # Set updater for any update
        if request and request.user:
            validated_data['updater'] = request.user

        # Call the parent update method to handle all field updates
        return super().update(instance, -validated_data)

    def to_representation(self, instance):

        """ Remove fields that are None or empty """

        data = super().to_representation(instance)
        data["result_fk_name"] = ResultsNameSerializer(instance.result_fk_name).data if instance.result_fk_name else None
        data["updater"] = UserListSerializer(instance.updater).data if instance.updater else None
        data['upload_file'] = FileUploadSerializer(instance.upload_file,context=self.context, many=True,).data
        data['student'] = StudentSerializer(instance.student,context=self.context).data
        data['teacher'] = UserListSerializer(instance.teacher,context=self.context).data
        return {key: value for key, value in data.items() if value not in [None, "", []]}
