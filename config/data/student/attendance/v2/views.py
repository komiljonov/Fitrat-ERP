from rest_framework.views import APIView
from rest_framework.request import HttpRequest, Request

from django.db import transaction

from data.student.attendance.models import Attendance
from data.student.attendance.v2.serializers import CreateAttendanceV2Serializer
from data.student.groups.models import Group
from data.student.homeworks.models import Homework, Homework_history
from data.student.mastering.models import Mastering
from data.student.quiz.models import Quiz
from data.student.studentgroup.models import StudentGroup
from data.student.subject.models import Theme

from rest_framework.response import Response


class AttendanceCreateAPIView(APIView):

    def post(self, request: HttpRequest | Request):

        serializer = CreateAttendanceV2Serializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        group: "Group" = data["group"]
        date = data["date"]
        theme: "Theme" = data["theme"]
        repeated = data["repeated"]

        items = data["items"]

        homework = Homework.objects.filter(theme=theme).first()
        quiz = Quiz.objects.filter(homework=homework).first()

        with transaction.atomic():
            for item in items:
                # student = item["student"]
                # lead = item["lead"]

                student: "StudentGroup" = item["student"]

                status = item["status"]
                comment = item.get("comment")

                attendance, created = Attendance.objects.update_or_create(
                    student=student.student,
                    lid=student.lid,
                    date=date,
                    group=group,
                    defaults=dict(
                        status=status,
                        comment=comment,
                        repeated=repeated,
                        first_lesson=student.first_lesson,
                    ),
                )

                attendance.theme.add(theme)

                if created:
                    if student != None and homework:
                        Homework_history.objects.create(
                            homework=homework,
                            student=student.student,
                            status="Passed",
                            mark=0,
                        )

                    mastering = Mastering.objects.create(
                        student=student.student,
                        lid=student.lid,
                        theme=theme,
                        test=quiz,
                        ball=0,
                    )

                    if theme.course.subject.is_language:

                        Mastering.objects.create(
                            student=student.student,
                            lid=student.lid,
                            theme=theme,
                            test=None,
                            choice="Speaking",
                            ball=0,
                        )

        return Response({"ok": True})
