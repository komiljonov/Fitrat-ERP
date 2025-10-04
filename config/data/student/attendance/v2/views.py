from django.db import transaction
from django.utils import timezone
from datetime import date as _date

from django.db.models import Q, Count

from rest_framework.views import APIView
from rest_framework.request import HttpRequest, Request

from rest_framework.generics import ListAPIView

from rest_framework.exceptions import NotFound


from data.student.attendance.models import Attendance
from data.student.attendance.v2.serializers import (
    AttendanceGroupStateSerializer,
    AttendanceThemeRequestSerializer,
    CreateAttendanceV2Serializer,
)
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

            lesson, created = group.lessons.update_or_create(
                date=date,
                defaults=dict(
                    theme=theme,
                    is_repeat=repeated,
                ),
            )

            for item in items:

                student_group: "StudentGroup" = item["student"]

                status = item["status"]
                comment = item.get("comment")

                attendance, created = Attendance.objects.update_or_create(
                    student_group=student_group,
                    student=student_group.student,
                    lead=student_group.lid,
                    date=date,
                    group=group,
                    defaults=dict(
                        status=status,
                        comment=comment,
                        first_lesson=student_group.first_lesson,
                    ),
                )

                if created:
                    if student_group.student != None and homework:
                        Homework_history.objects.create(
                            homework=homework,
                            student=student_group.student,
                            status="Passed",
                            mark=0,
                        )

                    mastering = Mastering.objects.create(
                        student=student_group.student,
                        lid=student_group.lid,
                        theme=theme,
                        test=quiz,
                        ball=0,
                    )

                    if theme.course.subject.is_language:

                        Mastering.objects.create(
                            student=student_group.student,
                            lid=student_group.lid,
                            theme=theme,
                            test=None,
                            choice="Speaking",
                            ball=0,
                        )

        return Response({"ok": True})


class AttendanceGroupStateAPIView(ListAPIView):

    serializer_class = AttendanceGroupStateSerializer

    pagination_class = None

    def get_queryset(self):
        group = Group.objects.filter(id=self.kwargs["group"]).first()

        if group is None:
            raise NotFound("Guruh topilmadi.")

        students = group.students.filter(is_archived=False)

        today = timezone.localdate()

        print(today)

        return students.select_related("student", "lid").exclude(
            Q(first_lesson__date__date__gt=today)
        )

    def get_serializer_context(self):

        context = super().get_serializer_context()

        attendances = Attendance.objects.filter(
            date=timezone.now().date(),
            group_id=self.kwargs["group"],
        )

        context["student_attendances"] = {
            a.student_id: a for a in attendances if a.student_id is not None
        }

        context["lead_attendances"] = {
            a.lead_id: a for a in attendances if a.lead_id is not None
        }

        return context


class AttendanceThemesAPIView(APIView):
    def get(self, request: HttpRequest):
        serializer = AttendanceThemeRequestSerializer(
            request.GET, data=request.query_params
        )
        serializer.is_valid(raise_exception=True)
        filters = serializer.validated_data

        group: "Group" = filters["group"]
        date = filters.get("date")

        themes_qs = group.course.themes.filter(level=group.level)
        theme_ids = list(themes_qs.values_list("id", flat=True))

        lessons = group.lessons.filter(Q(date__lt=date) if date else Q())

        # counts per theme for this group
        counts = lessons.values("theme_id").annotate(
            used_count=Count("id"),
            repeat_count=Count("id", filter=Q(is_repeat=True)),
        )
        counts_map = {c["theme_id"]: c for c in counts}

        # determine "today's" theme id
        if date:
            todays_theme_id = (
                group.lessons.filter(date=date)
                .values_list("theme_id", flat=True)
                .first()
            )
        else:
            last_non_repeat_theme_id = (
                lessons.filter(theme__isnull=False, is_repeat=False)
                .order_by("-date", "-id")
                .values_list("theme_id", flat=True)
                .first()
            )
            if last_non_repeat_theme_id in theme_ids:
                idx = theme_ids.index(last_non_repeat_theme_id)
                todays_theme_id = (
                    theme_ids[idx + 1] if idx + 1 < len(theme_ids) else None
                )
            else:
                todays_theme_id = (
                    theme_ids[0] if theme_ids else None
                )  # start from first if none used yet

        # build response list
        data = []
        for t in themes_qs.only("id", "title"):
            c = counts_map.get(t.id, {"used_count": 0, "repeat_count": 0})
            data.append(
                {
                    "id": t.id,
                    "title": t.title,
                    "was_used": c["used_count"] > 0,
                    "repeat_count": c["repeat_count"],
                    "is_today": (t.id == todays_theme_id),
                }
            )

        return Response(
            {
                "themes": data,
                "today_theme_id": todays_theme_id,  # optional helper
            }
        )
