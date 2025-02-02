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
            'all_themes',
            'label',
        ]

    def get_course(self, obj):
        return Course.objects.filter(subject=obj).count()

    def get_all_themes(self, obj):
        themes = Theme.objects.filter(subject=obj).count()
        return themes





class LevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Level
        fields = [
            'id',
            'name',
        ]


class ThemeSerializer(serializers.ModelSerializer):
    subject = serializers.PrimaryKeyRelatedField(queryset=Subject.objects.all())
    video = serializers.PrimaryKeyRelatedField(queryset=File.objects.all(), allow_null=True)
    file = serializers.PrimaryKeyRelatedField(queryset=File.objects.all(), allow_null=True)
    photo = serializers.PrimaryKeyRelatedField(queryset=File.objects.all(),allow_null=True)
    class Meta:
        model = Theme
        fields = [
            'id',
            'subject',
            'title',
            'description',
            'video',
            'file',
            'photo',
            'type',
        ]
    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['subject'] = SubjectSerializer(instance.subject).data
        rep['video'] = FileUploadSerializer(instance.video).data
        rep['file'] = FileUploadSerializer(instance.file).data
        rep['photo'] = FileUploadSerializer(instance.photo).data
        return rep