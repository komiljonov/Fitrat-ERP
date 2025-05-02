import pandas as pd
from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from icecream import ic
from numpy.ma.core import floor_divide
from rest_framework import status
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.generics import ListCreateAPIView, ListAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Subject, Level, Theme
# Create your views here.
from .serializers import SubjectSerializer, LevelSerializer, ThemeSerializer
from ..attendance.models import Attendance
from ..course.models import Course
from ..groups.models import Group
from ..homeworks.models import Homework


class SubjectList(ListCreateAPIView):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Subject.objects.all()
        filial = self.request.query_params.get('filial', None)
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
        filial = self.request.query_params.get('filial', None)
        if filial:
            queryset = queryset.filter(filial__id=filial)
        return queryset

    def get_paginated_response(self, data):
        return Response(data)


class LevelList(ListCreateAPIView):
    queryset = Level.objects.all()
    serializer_class = LevelSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        subject = self.request.query_params.get('subject', None)
        filial = self.request.query_params.get('filial', None)
        course = self.request.query_params.get('course', None)

        queryset = Level.objects.all()

        if course:
            queryset = queryset.filter(courses__id=course)

        if subject:
            queryset = queryset.filter(subject__id=subject)

        if filial:
            queryset = queryset.filter(filial__id=filial)
        return queryset


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
        filial = self.request.query_params.get('filial', None)
        subject = self.request.query_params.get('subject', None)

        queryset = Level.objects.all()

        if subject:
            queryset = queryset.filter(subject__id=subject)

        if filial:
            queryset = queryset.filter(filial__id=filial)
        return queryset

    def get_paginated_response(self, data):
        return Response(data)


class ThemeList(ListCreateAPIView):
    queryset = Theme.objects.all()
    serializer_class = ThemeSerializer
    permission_classes = [IsAuthenticated]


    def get_queryset(self):
        queryset = Theme.objects.all()

        theme = self.request.query_params.get('theme')
        level = self.request.query_params.get('level')
        if theme:
            queryset = queryset.filter(theme=theme)
        course = self.request.query_params.get('course')
        if course:
            queryset = queryset.filter(course__id=course)

        id = self.request.query_params.get('id')
        group_id = self.request.query_params.get('group')
        if group_id:
            try:
                group = Group.objects.get(id=group_id)
                queryset = queryset.filter(course=group.course)
            except Group.DoesNotExist:
                raise NotFound("Group not found.")


        if id:
            try:
                course = Group.objects.get(id=id)  # Agar id yo'q bo'lsa, xatolik qaytaradi
                queryset = queryset.filter(course=course.course)
            except Group.DoesNotExist:
                pass  # Agar Group topilmasa, filtr qo'llanilmaydi

        if level:
            queryset = queryset.filter(level__id=level)

        return queryset


class DynamicPageSizePagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class ThemePgList(ListCreateAPIView):
    serializer_class = ThemeSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = DynamicPageSizePagination

    def get_queryset(self):
        request = self.request
        search = request.query_params.get('search')
        theme_filter = request.query_params.get('theme')  # 'Lesson' or 'Repeat'
        group_id = request.query_params.get('group')

        qs = Theme.objects.filter(course=Group.objects.filter(id=group_id).first().course)

        if search:
            qs = qs.filter(title__icontains=search)

        if theme_filter and group_id:

            ic(theme_filter,group_id)

            last_att = Attendance.objects.filter(
                group__id=group_id,
                theme__theme=theme_filter,
            ).first()

            if last_att and last_att.theme.exists():
                last_theme = last_att.theme.order_by('-created_at').first()

                if last_theme:
                    # Only return the next one for 'Lesson', all for 'Repeat'
                    qs = Theme.objects.filter(
                        created_at__gt=last_theme.created_at,
                        theme=theme_filter,
                        course=last_theme.course
                    ).order_by('created_at')

                    if theme_filter == "Lesson":
                        return qs[:1]  # return only next one

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

        theme = self.request.query_params.get('theme')
        if theme:
            queryset = queryset.filter(theme=theme)

        group_id = self.request.query_params.get('id')
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
                name='file',
                in_=openapi.IN_FORM,
                type=openapi.TYPE_FILE,
                required=True,
                description='Excel (.xlsx) fayl',
            ),
        ],
        responses={
            201: openapi.Response(description="Import qilingan mavzular va uyga vazifalar"),
            400: "Xatolik yuz berdi",
            500: "Ichki server xatoligi",
        }
    )
    def post(self, request):
        file = request.FILES.get('file')

        if not file or not file.name.endswith(('.xlsx', '.xls')):
            return Response({'error': 'Excel fayl (.xlsx/.xls) yuboring'}, status=400)

        try:
            df = pd.read_excel(file)

            required_fields = {'Mavzu', 'Dars mazmuni', 'Uyga vazifa', 'Uyga vazifa mazmuni', 'Kurslar',"Daraja" ,'Fanlar'}
            if not required_fields.issubset(df.columns):
                return Response({
                    'error': f'Excel faylda quyidagi ustunlar bo\'lishi shart: {required_fields}'}, status=400)

            created = 0
            errors = []

            with transaction.atomic():
                for idx, row in df.iterrows():
                    course_name = str(row.get("Kurslar", "")).strip()
                    subject_name = str(row.get("Fanlar", "")).strip()
                    level_name = str(row.get("Daraja", "")).strip()

                    course = Course.objects.filter(name__icontains=course_name).first()
                    level = Level.objects.filter(name__icontains=level_name).first()
                    subject = Subject.objects.filter(name__icontains=subject_name).first()


                    if not course or not subject:
                        errors.append({
                            'row': idx + 2,
                            'error': f"Course yoki Subject topilmadi: {row['Course']}, {row['Subject']}"
                        })
                        continue

                    theme = Theme.objects.create(
                        title=row['Mavzu'],
                        description=row['Dars mazmuni'],
                        theme="Lesson",
                        course=course,
                        level=level,
                        subject=subject,
                    )

                    Homework.objects.create(
                        theme=theme,
                        title=row['Uyga vazifa'],
                        body=row['Uyga vazifa mazmuni'],
                    )
                    created += 1

            return Response({
                'message': f"{created} ta tema va uyga vazifa import qilindi",
                'errors': errors
            }, status=201)

        except Exception as e:
            return Response({'error': str(e)}, status=500)
