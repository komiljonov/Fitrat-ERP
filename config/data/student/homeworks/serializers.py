from django.db.models import Avg
from rest_framework import serializers
from .models import Homework, Homework_history
from ..subject.models import Theme
from ..subject.serializers import ThemeSerializer
from ...upload.models import File
from ...upload.serializers import FileUploadSerializer


class HomeworkSerializer(serializers.ModelSerializer):
    theme = serializers.PrimaryKeyRelatedField(queryset=Theme.objects.all(), allow_null=True)
    video = serializers.PrimaryKeyRelatedField(queryset=File.objects.all(), many=True, allow_null=True)
    documents = serializers.PrimaryKeyRelatedField(queryset=File.objects.all(), many=True, allow_null=True)
    photo = serializers.PrimaryKeyRelatedField(queryset=File.objects.all(), many=True, allow_null=True)
    ball = serializers.SerializerMethodField()

    class Meta:
        model = Homework
        fields = [
            "id",
            "title",
            "body",
            "theme",
            "video",
            "documents",
            "photo",
            "ball",
            "created_at"
        ]

    def get_ball(self, obj):
        histories = Homework_history.objects.filter(
            homework=obj,
            status="Passed",
            mark__gt=0
        )

        online_avg = histories.filter(homework__choice="Online").aggregate(avg=Avg("mark"))["avg"] or 0
        offline_avg = histories.filter(homework__choice="Offline").aggregate(avg=Avg("mark"))["avg"] or 0

        return {
            "online_avg": round(online_avg, 2),
            "offline_avg": round(offline_avg, 2),
            "overall_avg": round(histories.aggregate(avg=Avg("mark"))["avg"] or 0, 2)
        }


    def to_representation(self, instance):
        res = super().to_representation(instance)
        res["theme"] = ThemeSerializer(instance.theme, context=self.context).data if instance.theme else None
        res["video"] = FileUploadSerializer(instance.video.all(), many=True,context=self.context).data
        res["documents"] = FileUploadSerializer(instance.documents.all(), many=True,context=self.context).data
        res["photo"] = FileUploadSerializer(instance.photo.all(), many=True,context=self.context).data
        return res



class HomeworksHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Homework_history
        fields = [
            "id",
            "homework",
            "student",
            "status",
            "is_active",
            "mark",
            "created_at"
        ]