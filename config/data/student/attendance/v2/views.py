from typing import Dict
from django.db import transaction
from django.utils import timezone
from datetime import date as _date

from django.db.models import Q, Count

from rest_framework.views import APIView
from rest_framework.request import HttpRequest, Request

from rest_framework.generics import ListAPIView

from rest_framework.exceptions import NotFound
from rest_framework import status as rest_framwork_status


from data.student.attendance.models import Attendance
from data.student.attendance.v2.serializers import (
    AttendanceGroupStateSerializer,
    AttendanceThemeRequestSerializer,
    CreateAttendanceV2Serializer,
)
from data.student.subject.models import Level

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

            self._check_and_change_to_next_level(group)

        return Response(serializer.data, status=rest_framwork_status.HTTP_201_CREATED)

    def _check_and_change_to_next_level(self, group: "Group"):
        # Get all themes for the current level and course
        current_level_themes = Theme.objects.filter(
            course=group.course, level=group.level, is_archived=False
        ).order_by("order")

        if not current_level_themes.exists():
            return

        group_lessons = group.lessons.filter(is_repeat=False, theme__isnull=False)

        passed_themes = set(group_lessons.values_list("theme_id", flat=True))
        all_theme_ids = set(current_level_themes.values_list("id", flat=True))

        # If all themes are covered, handle level progression
        if len(passed_themes) >= len(all_theme_ids):
            # Get next level
            levels_qs = Level.objects.filter(
                courses=group.course, is_archived=False
            ).order_by("order")

            next_level = None

            if group.level is None:
                group.status = "INACTIVE"
                group.save(update_fields=["status"])
                return
            else:
                next_level = levels_qs.filter(order__gt=group.level.order).first()

            if next_level is None:
                group.status = "INACTIVE"
                group.save(update_fields=["status"])
            else:
                group.level = next_level
                group.save(update_fields=["level"])


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

        return students.select_related("student", "lid")

        # .exclude(
        #     Q(first_lesson__date__date__gt=today)
        # )

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
                "today_theme": todays_theme_id,  # optional helper
            }
        )


class AttendanceStatusForDateAPIView(APIView):

    def get(self, request: HttpRequest):

        serializer = AttendanceThemeRequestSerializer(
            request.GET, data=request.query_params
        )

        serializer.is_valid(raise_exception=True)

        filters = serializer.validated_data

        theme_response = self.themes(filters)

        status_response = self.get_status_response(filters)

        return Response(
            {
                **theme_response,
                # "themes": theme_response["themes"],
                # "today_theme": theme_response["today_theme"],
                # "is_repeat": theme_response["today_theme"],
                "statuses": status_response,
            }
        )

    def themes(self, filters: Dict):
        group: "Group" = filters["group"]
        date = filters.get("date", timezone.now().date())

        themes_qs = group.course.themes.filter(level=group.level, is_archived=False)
        theme_ids = list(
            themes_qs.filter(
                order__gte=(
                    group.start_theme.order
                    if group.start_theme and group.start_theme.level == group.level
                    else 0
                )
            ).values_list("id", flat=True)
        )

        # lessons strictly before the reference date (or all if date is falsy)
        lessons = group.lessons.filter(Q(date__lt=date) if date else Q())

        counts = lessons.values("theme_id").annotate(
            used_count=Count("id"),
            repeat_count=Count("id", filter=Q(is_repeat=True)),
        )
        counts_map = {c["theme_id"]: c for c in counts}

        todays_theme_id = None
        is_repeat_today = False

        # if a date is provided, only use that day's theme when it's actually selected
        today_lesson = None
        if date:
            today_lesson = (
                group.lessons.filter(date=date)
                .order_by("-id")
                .values("theme_id", "is_repeat")
                .first()
            )

        if today_lesson and today_lesson["theme_id"] is not None:
            # Respect explicitly selected theme for that date
            todays_theme_id = today_lesson["theme_id"]
            is_repeat_today = bool(today_lesson["is_repeat"])
        else:
            # Derive "next" theme relative to the date (or today if date is falsy)
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
                todays_theme_id = theme_ids[0] if theme_ids else None
            is_repeat_today = False  # derived "next" is never a repeat

        data = []
        for t in themes_qs.only("id", "title"):
            c = counts_map.get(t.id, {"used_count": 0, "repeat_count": 0})
            data.append(
                {
                    "id": t.id,
                    "title": t.title,
                    "was_used": c["used_count"] > 0,
                    "repeat_count": c["repeat_count"],
                    "skipped": (
                        t.order < group.start_theme.order
                        if group.start_theme
                        else False
                    ),
                    "is_today": (t.id == todays_theme_id),
                }
            )

        return {
            "today_theme": todays_theme_id,
            "is_repeat": is_repeat_today,
            "themes": data,
        }

    def get_serializer_context(self, filters: Dict):

        context = {"request": self.request}

        attendances = Attendance.objects.filter(
            date=filters.get("date", timezone.now().date()) or timezone.now().date(),
            group=filters["group"],
        )

        context["student_attendances"] = {
            a.student_id: a for a in attendances if a.student_id is not None
        }

        context["lead_attendances"] = {
            a.lead_id: a for a in attendances if a.lead_id is not None
        }

        return context

    def get_status_response(self, filters: Dict):

        # group = Group.objects.filter(id=self.kwargs["group"]).first()

        group: Group = filters["group"]

        students = group.students.filter(is_archived=False)

        today = timezone.localdate()

        print(today)

        students = students.select_related("student", "lid")

        return AttendanceGroupStateSerializer(
            students, context=self.get_serializer_context(filters), many=True
        ).data
