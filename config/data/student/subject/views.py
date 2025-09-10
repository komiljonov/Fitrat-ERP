import pandas as pd
from django.db import transaction
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from icecream import ic
from rest_framework.generics import (
    ListCreateAPIView,
    ListAPIView,
    RetrieveUpdateDestroyAPIView,
)
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Subject, Level, Theme

# Create your views here.
from .serializers import SubjectSerializer, LevelSerializer, ThemeSerializer
from data.student.attendance.models import Attendance
from data.student.course.models import Course
from data.student.groups.models import Group
from data.student.homeworks.models import Homework


class SubjectList(ListCreateAPIView):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Subject.objects.all()
        filial = self.request.GET.get("filial", None)
        is_language = self.request.GET.get("is_language", None)
        is_archived = self.request.GET.get("is_archived", None)

        if is_archived:
            queryset = queryset.filter(is_archived=is_archived.capitalize())
        if is_language:
            queryset = queryset.filter(is_language=is_language.capitalize())
        if filial:
            queryset = queryset.filter(filial=filial)

        return queryset


class SubjectDetail(RetrieveUpdateDestroyAPIView):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    permission_classes = [IsAuthenticated]


class SubjectNoPG(ListAPIView):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        queryset = Subject.objects.all()
        filial = self.request.GET.get("filial", None)
        if filial:
            queryset = queryset.filter(filial_id=filial)
        return queryset

    def get_paginated_response(self, data):
        return Response(data)


class LevelList(ListCreateAPIView):
    queryset = Level.objects.all()
    serializer_class = LevelSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        subject = self.request.GET.get("subject", None)
        filial = self.request.GET.get("filial", None)
        course = self.request.GET.get("course", None)
        is_archived = self.request.GET.get("is_archived", None)

        queryset = Level.objects.all()

        if is_archived:
            queryset = queryset.filter(is_archived=is_archived.capitalize())

        if course:
            queryset = queryset.filter(courses_id=course)

        if subject:
            queryset = queryset.filter(subject_id=subject)

        if filial:
            queryset = queryset.filter(filial_id=filial)
        return queryset.order_by("order")


class LevelDetail(RetrieveUpdateDestroyAPIView):
    queryset = Level.objects.all()
    serializer_class = LevelSerializer
    permission_classes = [IsAuthenticated]


class LevelNoPG(ListAPIView):
    queryset = Level.objects.all()
    serializer_class = LevelSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        filial = self.request.GET.get("filial", None)
        subject = self.request.GET.get("subject", None)
        is_archived = self.request.GET.get("is_archived", None)

        queryset = Level.objects.all()

        if is_archived:
            queryset = queryset.filter(is_archived=is_archived.capitalize())

        if subject:
            queryset = queryset.filter(subject_id=subject)

        if filial:
            queryset = queryset.filter(filial_id=filial)
        return queryset

    def get_paginated_response(self, data):
        return Response(data)


class ThemeList(ListCreateAPIView):
    queryset = Theme.objects.all()
    serializer_class = ThemeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Theme.objects.all()

        theme = self.request.GET.get("theme")
        level = self.request.GET.get("level")
        is_archived = self.request.GET.get("is_archived", None)

        if is_archived:
            queryset = queryset.filter(is_archived=is_archived.capitalize())
        if theme:
            queryset = queryset.filter(theme=theme)
        course = self.request.GET.get("course")
        if course:
            queryset = queryset.filter(course_id=course)

        id = self.request.GET.get("id")
        group_id = self.request.GET.get("group")
        if group_id:
            try:
                group = Group.objects.get(id=group_id)
                queryset = queryset.filter(course=group.course)
            except Group.DoesNotExist:
                raise NotFound("Group not found.")

        if id:
            try:
                course = Group.objects.get(
                    id=id
                )  # Agar id yo'q bo'lsa, xatolik qaytaradi
                queryset = queryset.filter(course=course.course)
            except Group.DoesNotExist:
                pass  # Agar Group topilmasa, filtr qo'llanilmaydi

        if level:
            queryset = queryset.filter(level_id=level)

        return queryset


class DynamicPageSizePagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


class ThemePgList(ListCreateAPIView):
    serializer_class = ThemeSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = DynamicPageSizePagination

    def get_queryset(self):
        request = self.request
        search = request.GET.get("search")
        theme_filter = request.GET.get("theme")  # 'Lesson' or 'Repeat'
        group_id = request.GET.get("group")

        ic(group_id, theme_filter)

        if group_id:
            group = Group.objects.filter(id=group_id).first()
            if not group or not group.course:
                return Theme.objects.none()

            qs = Theme.objects.filter(course=group.course).order_by("created_at")
        else:
            qs = Theme.objects.all()

        if search:
            qs = qs.filter(title__icontains=search)

        if theme_filter and group_id:
            # Check if there are any attendance records for this group
            attendance_count = Attendance.objects.filter(group_id=group_id).count()

            if theme_filter == "Repeat":
                if attendance_count == 0:
                    return Theme.objects.none()

                # Get themes that have been used in attendance records for this group
                attendance_qs = Attendance.objects.filter(group_id=group_id).exclude(
                    theme__isnull=True
                )

                ic(attendance_qs.all())

                if not attendance_qs.exists():
                    return Theme.objects.none()

                # Get unique theme IDs from attendance records
                theme_ids = attendance_qs.values_list("theme__id", flat=True).distinct()
                ic(theme_ids)

                # Return only themes that have been used in attendance
                return Theme.objects.filter(id__in=theme_ids).order_by("created_at")

            elif theme_filter == "Lesson":
                if attendance_count == 0:
                    # Return first theme if no attendance records exist
                    first_theme = qs.first()
                    if first_theme:
                        return Theme.objects.filter(id=first_theme.id)
                    else:
                        return Theme.objects.none()

                # Find the last attendance record for this group
                last_att = (
                    Attendance.objects.filter(group_id=group_id)
                    .exclude(theme__isnull=True)
                    .order_by("-created_at")
                    .first()
                )

                if last_att and last_att.theme.exists():
                    last_theme = last_att.theme.order_by("-created_at").first()

                    if last_theme:
                        next_theme = qs.filter(
                            created_at__gt=last_theme.created_at
                        ).first()
                        if next_theme:
                            return Theme.objects.filter(id=next_theme.id)
                        else:
                            return Theme.objects.none()

                first_theme = qs.first()
                if first_theme:
                    return Theme.objects.filter(id=first_theme.id)
                else:
                    return Theme.objects.none()

        return qs


class ThemeDetail(RetrieveUpdateDestroyAPIView):
    queryset = Theme.objects.all()
    serializer_class = ThemeSerializer
    permission_classes = [IsAuthenticated]


from rest_framework.exceptions import NotFound


class ThemeNoPG(ListAPIView):
    serializer_class = ThemeSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        queryset = Theme.objects.all()

        theme = self.request.GET.get("theme")
        if theme:
            queryset = queryset.filter(theme=theme)

        group_id = self.request.GET.get("id")
        if group_id:
            try:
                group = Group.objects.get(id=group_id)
                queryset = queryset.filter(course=group.course)
            except Group.DoesNotExist:
                raise NotFound("Group not found.")

        return queryset

    def get_paginated_response(self, data):
        return Response(data)


class ImportStudentsAPIView(APIView):
    parser_classes = [MultiPartParser]

    @swagger_auto_schema(
        operation_summary="Exceldan studentlar import qilish",
        manual_parameters=[
            openapi.Parameter(
                name="file",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_FILE,
                required=True,
                description="Excel (.xlsx) fayl",
            ),
        ],
        responses={
            201: openapi.Response(
                description="Import qilingan mavzular va uyga vazifalar"
            ),
            400: "Xatolik yuz berdi",
            500: "Ichki server xatoligi",
        },
    )
    def post(self, request):
        file = request.FILES.get("file")

        if not file or not file.name.endswith((".xlsx", ".xls")):
            return Response({"error": "Excel fayl (.xlsx/.xls) yuboring"}, status=400)

        try:
            df = pd.read_excel(file)

            required_fields = {
                "Mavzu",
                "Dars mazmuni",
                "Uyga vazifa",
                "Uyga vazifa mazmuni",
                "Kurslar",
                "Daraja",
                "Fanlar",
            }
            if not required_fields.issubset(df.columns):
                return Response(
                    {
                        "error": f"Excel faylda quyidagi ustunlar bo'lishi shart: {required_fields}"
                    },
                    status=400,
                )

            created = 0
            errors = []

            with transaction.atomic():
                for idx, row in df.iterrows():
                    course_name = str(row.get("Kurslar", "")).strip()
                    subject_name = str(row.get("Fanlar", "")).strip()
                    level_name = str(row.get("Daraja", "")).strip()

                    course = Course.objects.filter(name__icontains=course_name).first()
                    level = Level.objects.filter(
                        name__iexact=level_name, courses=course
                    ).first()
                    subject = Subject.objects.filter(name__iexact=subject_name).first()

                    if not course or not subject:
                        errors.append(
                            {
                                "row": idx + 2,
                                "error": f"Course yoki Subject topilmadi: {course_name}, {subject_name}",
                            }
                        )
                        continue

                    theme = Theme.objects.create(
                        title=row["Mavzu"],
                        description=row["Dars mazmuni"],
                        theme="Lesson",
                        course=course,
                        level=level,
                        subject=subject,
                    )

                    Homework.objects.create(
                        theme=theme,
                        title=row["Uyga vazifa"],
                        body=row["Uyga vazifa mazmuni"],
                    )
                    created += 1

            return Response(
                {
                    "message": f"{created} ta tema va uyga vazifa import qilindi",
                    "errors": errors,
                },
                status=201,
            )

        except Exception as e:
            return Response({"error": str(e)}, status=500)
