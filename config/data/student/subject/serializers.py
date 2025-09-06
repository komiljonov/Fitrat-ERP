from rest_framework import serializers

from .models import Subject, Level, Theme
from data.student.course.models import Course
from data.upload.models import File
from data.upload.serializers import FileUploadSerializer


class ThemeDumpSerializer(serializers.ModelSerializer):
    class Meta:
        model = Theme
        fields = "__all__"


class ThemeLoaddataSerializer(serializers.ModelSerializer):
    class Meta:
        model = Theme
        fields = "__all__"
        extra_kwargs = {
            "created_at": {"required": False},
            "updated_at": {"required": False},
            "deleted_at": {"required": False},
            "id": {"required": False},
        }


class SubjectSerializer(serializers.ModelSerializer):
    course = serializers.SerializerMethodField()
    all_themes = serializers.SerializerMethodField()
    image = serializers.PrimaryKeyRelatedField(
        queryset=File.objects.all(), allow_null=True
    )

    class Meta:
        model = Subject
        fields = [
            "id",
            "name",
            "course",
            "has_level",
            "is_language",
            "image",
            "all_themes",
            "label",
            "is_archived",
        ]

    def create(self, validated_data):
        filial = validated_data.pop("filial", None)
        if not filial:
            request = self.context.get("request")  #
            if request and hasattr(request.user, "filial"):
                filial = request.user.filial.first()

        if not filial:
            raise serializers.ValidationError(
                {"filial": "Filial could not be determined."}
            )

        room = Subject.objects.create(filial=filial, **validated_data)
        return room

    def get_course(self, obj):
        return Course.objects.filter(subject=obj, is_archived=False).count()

    def get_all_themes(self, obj: Subject):

        # themes = Theme.objects.filter(
        #     subject=obj, is_archived=False, level__is_archived=False
        # ).count()
        themes = obj.themes.filter(
            course__is_archived=False,
            level__is_archived=False,
            is_archived=False,
        ).count()

        return themes

    def to_representation(self, instance):

        rep = super().to_representation(instance)
        rep["image"] = FileUploadSerializer(instance.image, context=self.context).data
        return rep


class LevelSerializer(serializers.ModelSerializer):
    subject = serializers.PrimaryKeyRelatedField(
        queryset=Subject.objects.all(), allow_null=True
    )
    all_themes = serializers.SerializerMethodField()

    class Meta:
        model = Level
        fields = [
            "id",
            "name",
            "subject",
            "courses",
            "all_themes",
            "order",
            "is_archived",
        ]

    def get_all_themes(self, obj):
        themes = Theme.objects.filter(level=obj, is_archived=False).count()
        return themes

    def to_representation(self, obj):
        rep = super().to_representation(obj)
        rep["subject"] = SubjectSerializer(obj.subject).data
        return rep


class ThemeSerializer(serializers.ModelSerializer):
    subject = serializers.PrimaryKeyRelatedField(queryset=Subject.objects.all())

    homework_files = serializers.PrimaryKeyRelatedField(
        queryset=File.objects.all(),
        many=True,
        allow_null=True,
    )
    repeated_theme = serializers.PrimaryKeyRelatedField(
        queryset=Theme.objects.all(),
        many=True,
        allow_null=True,
    )
    course_work_files = serializers.PrimaryKeyRelatedField(
        queryset=File.objects.all(),
        many=True,
        allow_null=True,
    )
    extra_work_files = serializers.PrimaryKeyRelatedField(
        queryset=File.objects.all(),
        many=True,
        allow_null=True,
    )

    videos = serializers.PrimaryKeyRelatedField(
        queryset=File.objects.all(),
        many=True,
        allow_null=True,
        required=False,
    )
    files = serializers.PrimaryKeyRelatedField(
        queryset=File.objects.all(),
        many=True,
        allow_null=True,
        required=False,
    )
    photos = serializers.PrimaryKeyRelatedField(
        queryset=File.objects.all(),
        many=True,
        allow_null=True,
        required=False,
    )

    def __init__(self, *args, **kwargs):
        fields_to_remove: list | None = kwargs.pop("remove_fields", None)
        include_only: list | None = kwargs.pop("include_only", None)

        if fields_to_remove and include_only:
            raise ValueError(
                "You cannot use 'remove_fields' and 'include_only' at the same time."
            )

        super(ThemeSerializer, self).__init__(*args, **kwargs)

        if include_only is not None:
            allowed = set(include_only)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)

        elif fields_to_remove:
            for field_name in fields_to_remove:
                self.fields.pop(field_name, None)

    class Meta:
        model = Theme
        fields = [
            "id",
            "subject",
            "title",
            "theme",
            "repeated_theme",
            "course",
            "level",
            "description",
            "videos",
            "files",
            "photos",
            "is_archived",
            "homework_files",
            "course_work_files",
            "extra_work_files",
        ]

    def get_course(self, obj):
        return list(
            Course.objects.filter(subject=obj.subject).values("id", "groups_course__id")
        )

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["subject"] = SubjectSerializer(instance.subject, context=self.context).data

        rep["repeated_theme"] = ThemeSerializer(
            instance.repeated_theme.all(), many=True, context=self.context
        ).data

        rep["videos"] = FileUploadSerializer(
            instance.videos.all(), many=True, context=self.context
        ).data

        rep["files"] = FileUploadSerializer(
            instance.files.all(), many=True, context=self.context
        ).data

        rep["photos"] = FileUploadSerializer(
            instance.photos.all(), many=True, context=self.context
        ).data

        rep["course_work_files"] = FileUploadSerializer(
            instance.course_work_files, many=True, context=self.context
        ).data

        rep["homework_files"] = FileUploadSerializer(
            instance.homework_files, many=True, context=self.context
        ).data

        rep["extra_work_files"] = FileUploadSerializer(
            instance.extra_work_files, many=True, context=self.context
        ).data

        rep["course"] = self.get_course(instance)
        return rep
