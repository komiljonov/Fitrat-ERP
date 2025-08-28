from statistics import mean

from rest_framework import serializers
from .models import Homework, Homework_history
from data.student.attendance.models import Attendance
from data.student.mastering.models import Mastering
from data.student.student.models import Student
from data.student.subject.models import Theme
from data.student.subject.serializers import ThemeSerializer
from data.upload.models import File
from data.upload.serializers import FileUploadSerializer


class HomeworkSerializer(serializers.ModelSerializer):
    theme = serializers.PrimaryKeyRelatedField(
        queryset=Theme.objects.all(),
        allow_null=True,
    )
    video = serializers.PrimaryKeyRelatedField(
        queryset=File.objects.all(),
        many=True,
        allow_null=True,
    )
    documents = serializers.PrimaryKeyRelatedField(
        queryset=File.objects.all(),
        many=True,
        allow_null=True,
    )
    photo = serializers.PrimaryKeyRelatedField(
        queryset=File.objects.all(),
        many=True,
        allow_null=True,
    )
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
            "choice",
            "test_checked",
            "is_active",
            "created_at",
        ]

    def get_ball(self, obj):
        request = self.context.get("request")
        student_id = request.query_params.get("student") if request else None
        user_id = request.query_params.get("user") if request else None

        if not student_id and not user_id:
            return None

        student = None
        if user_id:
            student = Student.objects.filter(user__id=user_id).first()
        if student_id:
            student = Student.objects.filter(id=student_id).first()

        if not student:
            return None

        histories = Homework_history.objects.filter(
            student=student,
            homework=obj,
        )

        mastering = Mastering.objects.filter(
            student=student, choice="Test", theme=obj.theme
        ).first()

        mastering_ball = (
            mastering.ball if mastering and mastering.ball is not None else None
        )

        online_marks = list(
            histories.filter(homework__choice="Online").values_list("mark", flat=True)
        )
        offline_marks = list(
            histories.filter(homework__choice="Offline").values_list("mark", flat=True)
        )
        all_marks = list(histories.values_list("mark", flat=True))

        if mastering_ball is not None:
            all_marks.append(mastering_ball)

        online_avg = mean(online_marks) if online_marks else 0
        offline_avg = mean(offline_marks) if offline_marks else 0
        overall_avg = round(mean(all_marks), 2) if all_marks else 0

        if overall_avg == 0:
            ball = 0
        elif overall_avg <= 20:
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
            "overall_avg": overall_avg,
            "ball": round(ball, 2),
        }

    def get_is_active(self, obj):
        att = Attendance.objects.filter(theme=obj.theme).first()

        if att:
            return True
        return False

    def to_representation(self, instance):
        res = super().to_representation(instance)
        res["theme"] = (
            ThemeSerializer(instance.theme, context=self.context).data
            if instance.theme
            else None
        )
        res["video"] = FileUploadSerializer(
            instance.video.all(), many=True, context=self.context
        ).data
        res["documents"] = FileUploadSerializer(
            instance.documents.all(), many=True, context=self.context
        ).data
        res["photo"] = FileUploadSerializer(
            instance.photo.all(), many=True, context=self.context
        ).data
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
            "test_checked",
            "created_at",
        ]

    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)
        instance.updater = self.context["request"].user
        instance.save()
        return instance
