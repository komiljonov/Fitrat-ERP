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
    video = serializers.PrimaryKeyRelatedField(queryset=File.objects.all(), many=True, allow_null=True, required=False)
    file = serializers.PrimaryKeyRelatedField(queryset=File.objects.all(), many=True, allow_null=True, required=False)
    photo = serializers.PrimaryKeyRelatedField(queryset=File.objects.all(), many=True, allow_null=True, required=False)

    class Meta:
        model = Theme
        fields = [
            'id',
            'subject',
            'title',
            'theme',
            'course',
            'description',
            'video',
            'file',
            'photo',
            'type',
        ]

    def get_course(self, obj):
        return list(Course.objects.filter(subject=obj.subject).values('id', 'group__id'))

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['subject'] = SubjectSerializer(instance.subject).data
        rep['video'] = FileUploadSerializer(instance.video.all(), many=True,context=self.context).data
        rep['file'] = FileUploadSerializer(instance.file.all(), many=True,context=self.context).data
        rep['photo'] = FileUploadSerializer(instance.photo.all(), many=True,context=self.context).data
        rep['course'] = self.get_course(instance)
        return rep
