from django.db.models import Avg
from rest_framework import serializers
from .models import Homework, Homework_history
from ..attendance.models import Attendance
from ..subject.models import Theme
from ..subject.serializers import ThemeSerializer
from ...upload.models import File
from ...upload.serializers import FileUploadSerializer


class HomeworkSerializer(serializers.ModelSerializer):
    theme = serializers.PrimaryKeyRelatedField(queryset=Theme.objects.all(), allow_null=True)
    video = serializers.PrimaryKeyRelatedField(queryset=File.objects.all(), many=True, allow_null=True)
    documents = serializers.PrimaryKeyRelatedField(queryset=File.objects.all(), many=True, allow_null=True)
    photo = serializers.PrimaryKeyRelatedField(queryset=File.objects.all(), many=True, allow_null=True)
    is_active = serializers.SerializerMethodField()
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
            "is_active",
            "created_at"
        ]

    def get_ball(self, obj):
        request = self.context.get("request")
        student_id = request.query_params.get("student") if request else None

        if not student_id:
            return None

        histories = Homework_history.objects.filter(
            student__id=student_id,
            homework=obj,
            status="Passed",
            mark__gt=0
        )

        online_avg = histories.filter(homework__choice="Online").aggregate(avg=Avg("mark"))["avg"] or 0
        offline_avg = histories.filter(homework__choice="Offline").aggregate(avg=Avg("mark"))["avg"] or 0

        overall_avg = round(histories.aggregate(avg=Avg("mark"))["avg"] or 0, 2)

        if overall_avg <= 20:
            ball = 1
        elif overall_avg <= 40:
            ball = 2
        elif overall_avg <= 60:
            ball = 3
        elif overall_avg <= 80:
            ball = 4
        else:
            ball = 5
        return {
            "online_avg": round(online_avg, 2),
            "offline_avg": round(offline_avg, 2),
            "overall_avg": round(histories.aggregate(avg=Avg("mark"))["avg"] or 0, 2),
            "ball": round(ball, 2),
        }

    def get_is_active(self, obj):
        att = Attendance.objects.filter(
            theme=obj.theme
        ).first()

        if att:
            return True
        return False

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
            "description",
            "mark",
            "created_at"
        ]