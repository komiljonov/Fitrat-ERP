from django.utils.module_loading import import_string
from rest_framework import serializers

from .models import Subject,Level,Theme
from ..course.models import Course
from ...upload.models import File
from ...upload.serializers import FileUploadSerializer


class SubjectSerializer(serializers.ModelSerializer):
    course = serializers.SerializerMethodField()
    all_themes = serializers.SerializerMethodField()
    class Meta:
        model = Subject
        fields = [
            'id',
            'name',
            'course',
            'has_level',
            'all_themes',
            'label',
        ]

    def create(self, validated_data):
        filial = validated_data.pop("filial", None)
        if not filial:
            request = self.context.get("request")  #
            if request and hasattr(request.user, "filial"):
                filial = request.user.filial.first()

        if not filial:
            raise serializers.ValidationError({"filial": "Filial could not be determined."})

        room = Subject.objects.create(filial=filial, **validated_data)
        return room


    def get_course(self, obj):
        return Course.objects.filter(subject=obj).count()

    def get_all_themes(self, obj):
        themes = Theme.objects.filter(subject=obj).count()
        return themes





class LevelSerializer(serializers.ModelSerializer):
    subject = serializers.PrimaryKeyRelatedField(queryset=Subject.objects.all(),allow_null=True)
    all_themes = serializers.SerializerMethodField()
    class Meta:
        model = Level
        fields = [
            'id',
            'name',
            'subject',
            "courses",
            "all_themes",
        ]

    def get_all_themes(self, obj):
        themes = Theme.objects.filter(subject=obj.subject).count()
        return themes


    def to_representation(self, obj):
        rep = super().to_representation(obj)
        rep["subject"] = SubjectSerializer(obj.subject).data
        return rep





class ThemeSerializer(serializers.ModelSerializer):
    subject = serializers.PrimaryKeyRelatedField(queryset=Subject.objects.all())

    homework_files = serializers.PrimaryKeyRelatedField(queryset=File.objects.all(),many=True ,allow_null=True)
    repeated_theme = serializers.PrimaryKeyRelatedField(queryset=Theme.objects.all(), many=True,allow_null=True)
    course_work_files = serializers.PrimaryKeyRelatedField(queryset=File.objects.all(),many=True,allow_null=True)
    extra_work_files = serializers.PrimaryKeyRelatedField(queryset=File.objects.all(),many=True,allow_null=True)

    videos = serializers.PrimaryKeyRelatedField(queryset=File.objects.all(), many=True, allow_null=True, required=False)
    files = serializers.PrimaryKeyRelatedField(queryset=File.objects.all(), many=True, allow_null=True, required=False)
    photos = serializers.PrimaryKeyRelatedField(queryset=File.objects.all(), many=True, allow_null=True, required=False)

    class Meta:
        model = Theme
        fields = [
            'id',
            'subject',
            'title',
            'theme',
            "repeated_theme",
            'course',
            'description',
            'videos',
            'files',
            'photos',

            'homework_files',
            'course_work_files',
            'extra_work_files',
        ]

    def get_course(self, obj):
        return list(Course.objects.filter(subject=obj.subject).values('id', 'group__id'))

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['subject'] = SubjectSerializer(instance.subject).data
        rep["repeated_theme"] = ThemeSerializer(instance.repeated_theme.all(),many=True,context=self.context).data
        rep['videos'] = FileUploadSerializer(instance.videos.all(), many=True,context=self.context).data
        rep['files'] = FileUploadSerializer(instance.files.all(), many=True,context=self.context).data
        rep['photos'] = FileUploadSerializer(instance.photos.all(), many=True,context=self.context).data

        rep['course_work_files'] = FileUploadSerializer(instance.course_work_files, many=True,context=self.context).data
        rep['homework_files'] = FileUploadSerializer(instance.homework_files, many=True,context=self.context).data
        rep['extra_work_files'] = FileUploadSerializer(instance.extra_work_files, many=True,context=self.context).data

        rep['course'] = self.get_course(instance)
        return rep
