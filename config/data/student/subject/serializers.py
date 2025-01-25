from rest_framework import serializers

from .models import Subject,Level,Theme
from ...upload.models import File
from ...upload.serializers import FileUploadSerializer


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = [
            'id',
            'name',
            'label',
        ]

class LevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Level
        fields = [
            'id',
            'name',
        ]


class ThemeSerializer(serializers.ModelSerializer):
    subject = serializers.PrimaryKeyRelatedField(queryset=Subject.objects.all())
    video = serializers.PrimaryKeyRelatedField(queryset=File.objects.all())
    file = serializers.PrimaryKeyRelatedField(queryset=File.objects.all())
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