from datetime import datetime, timedelta

from django.db import transaction
from django.utils import timezone
from django.core.exceptions import FieldError
from django.db.models import Q, Sum, Value, F
from django.db.models.functions import Coalesce
from django.http import HttpRequest, HttpResponse
from django.utils.dateparse import parse_datetime
from django.db.models import Case, When, IntegerField, FloatField

from rest_framework.exceptions import NotFound
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.generics import (
    RetrieveUpdateDestroyAPIView,
    ListAPIView,
    ListCreateAPIView,
    CreateAPIView,
    UpdateAPIView,
)
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from django_filters.rest_framework import DjangoFilterBackend

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from openpyxl import Workbook
from openpyxl.styles import Font, Alignment


from data.archive.models import Archive
from data.lid.archived.models import Archived
from data.student.lesson.models import FirstLLesson

from .models import Lid
from .serializers import LeadArchiveSerializer, LeadSerializer


class CustomPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100


class LeadListCreateView(ListCreateAPIView):
    serializer_class = LeadSerializer
    pagination_class = CustomPagination
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]

    # search_fields = ["first_name", "last_name", "phone_number", ]
    # filterset_fields = [
    #     "student_type",
    #     "education_lang",
    #     "filial",
    #     "marketing_channel",
    #     "lid_stage_type",
    #     "lid_stages",
    #     "ordered_stages",
    #     "is_dubl",
    #     "is_archived",
    # ]

    def get_serializer(self, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        kwargs.setdefault("context", self.get_serializer_context())

        # Only add include_only if the request is GET (or exclude if it's POST)
        if self.request.method == "GET":
            kwargs["include_only"] = [
                "id",
                "first_name",
                "last_name",
                "middle_name",
                "photo",
                "phone_number",
                "filial",
                "lid_stages",
                "lid_stage_type",
                "ordered_stages",
                "call_operator",
                "sales_manager",
                "is_archived",
                "ordered_date",
                "created_at",
            ]

        return serializer_class(*args, **kwargs)

    def get_queryset(self):
        user = self.request.user

        if user.is_anonymous:
            return Lid.objects.none()

        queryset = Lid.objects.all()
        # filial = self.request.GET.get("filial")

        if user.role == "CALL_OPERATOR" or user.is_call_center:
            queryset = queryset.filter(
                Q(filial__in=user.filial.all()) | Q(filial__isnull=True),
                Q(call_operator=user) | Q(call_operator__isnull=True),
            )
        else:
            queryset = queryset.filter(
                Q(filial__in=user.filial.all()) | Q(filial__isnull=True)
            )

        # ✅ Additional Filters
        is_archived = self.request.GET.get("is_archived")
        search_term = self.request.GET.get("search", "")
        course_id = self.request.GET.get("course")
        call_operator_id = self.request.GET.get("call_operator")
        service_manager = self.request.GET.get("service_manager")
        sales_manager = self.request.GET.get("sales_manager")
        teacher = self.request.GET.get("teacher")
        channel = self.request.GET.get("channel")
        subject = self.request.GET.get("subject")
        is_student = self.request.GET.get("is_student")
        lid_stage_type = self.request.GET.get("lid_stage_type")
        no_first_lesson = self.request.GET.get("no_first_lesson")
        ordered_stages = self.request.GET.get("ordered_stages")
        lead_stages = self.request.GET.get("lid_stages")
        marketing_channel = self.request.GET.get("marketing_channel")

        # order_by = self.request.GET.get("order_by")

        if marketing_channel:
            queryset = queryset.filter(marketing_channel_id=marketing_channel)
        if lead_stages:
            queryset = queryset.filter(lid_stages=lead_stages)
        if ordered_stages:
            queryset = queryset.filter(ordered_stages=ordered_stages)
        if no_first_lesson:
            queryset = queryset.filter().exclude(
                ordered_stages="BIRINCHI_DARS_BELGILANGAN"
            )
        if lid_stage_type:
            queryset = queryset.filter(lid_stage_type=lid_stage_type)
        if is_archived:
            queryset = queryset.filter(is_archived=is_archived.capitalize())

        if channel:
            queryset = queryset.filter(marketing_channel_id=channel)

        if service_manager:
            queryset = queryset.filter(service_manager_id=service_manager)

        if sales_manager:
            queryset = queryset.filter(sales_manager_id=sales_manager)

        if teacher:
            queryset = queryset.filter(groups__group__teacher_id=teacher)

        if subject:
            queryset = queryset.filter(subject_id=subject)

        if is_student == "false":
            queryset = queryset.filter(is_student=False)

        if call_operator_id:
            queryset = queryset.filter(call_operator_id=call_operator_id)

        if course_id:
            queryset = queryset.filter(groups__group__course_id=course_id)

        if search_term:
            try:
                queryset = queryset.filter(
                    Q(first_name__icontains=search_term)
                    | Q(last_name__icontains=search_term)
                    | Q(phone_number__icontains=search_term)
                )
            except FieldError as e:
                print(f"FieldError: {e}")

        start_date_str = self.request.GET.get("start_date")
        end_date_str = self.request.GET.get("end_date")

        date_format = "%Y-%m-%d"

        if start_date_str and end_date_str:
            start_date = datetime.strptime(start_date_str, date_format).date()
            end_date = datetime.strptime(end_date_str, date_format).date()

            start_datetime = datetime.combine(start_date, datetime.min.time())
            end_datetime = datetime.combine(end_date, datetime.min.time()) + timedelta(
                days=1
            )

            queryset = queryset.filter(
                created_at__gte=start_datetime, created_at__lt=end_datetime
            )

        elif start_date_str:
            # only filter 1 day if end_date is not present
            start_date = datetime.strptime(start_date_str, date_format).date()
            start_datetime = datetime.combine(start_date, datetime.min.time())
            end_datetime = start_datetime + timedelta(days=1)

            queryset = queryset.filter(
                created_at__gte=start_datetime, created_at__lt=end_datetime
            )

        # if order_by:
        # if order_by in ["order_index", "-order_index"]:
        queryset = queryset.annotate(
            order_index=Case(
                When(lid_stages="YANGI_LEAD", then=1),
                default=0,
                output_field=IntegerField(),
            )
        ).order_by(
            # order_by
            "-order_index",
            "-created_at",
        )  # '-' if you want YANGI_LEAD first

        return queryset


class OrderListCreateView(LeadListCreateView):

    def get_queryset(self):

        queryset = super().get_queryset()

        queryset = queryset.annotate(
            order_index=Case(
                When(ordered_stages="YANGI_BUYURTMA", then=1),
                When(ordered_stages="BIRINCHI_DARS_BELGILANGAN", then=2),
                When(ordered_stages="YANGI_BUYURTMA", then=3),
                default=0,
                output_field=IntegerField(),
            )
        ).order_by(
            # order_by
            "-order_index",
            "-created_at",
        )  # '-' if you want YANGI_LEAD first

        queryset.order_by("")


class LeadRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    serializer_class = LeadSerializer
    queryset = Lid.objects.all()
    permission_classes = [IsAuthenticated]


class LeadListNoPG(ListAPIView):
    queryset = Lid.objects.all()
    serializer_class = LeadSerializer
    pagination_class = None

    def get_queryset(self):
        filial = self.request.GET.get("filial")
        is_archived = self.request.GET.get("is_archived")
        # search_term = self.request.GET.get("search", "")
        # course_id = self.request.GET.get("course")
        # call_operator_id = self.request.GET.get("call_operator")
        # service_manager = self.request.GET.get("service_manager")
        # sales_manager = self.request.GET.get("sales_manager")
        # teacher = self.request.GET.get("teacher")
        # channel = self.request.GET.get("channel")
        # subject = self.request.GET.get("subject")
        is_student = self.request.GET.get("is_student")
        lid_stage_type = self.request.GET.get("lid_stage_type")
        # no_first_lesson = self.request.GET.get("no_first_lesson")
        ordered_stages = self.request.GET.get("ordered_stages")
        lid_stages = self.request.GET.get("lid_stages")
        # marketing_channel = self.request.GET.get("marketing_channel")

        # order_by = self.request.GET.get("order_by")

        queryset = Lid.objects.all()

        if lid_stage_type:
            queryset = queryset.filter(lid_stage_type=lid_stage_type)

        if ordered_stages:
            queryset = queryset.filter(ordered_stages=ordered_stages)

        if lid_stages:
            queryset = queryset.filter(lid_stages=lid_stages)

        if is_archived:
            queryset = queryset.filter(is_archived=is_archived.capitalize())

        if filial:
            queryset = queryset.filter(filial__id=filial)

        if is_student:
            queryset = queryset.filter(is_student=is_student.capitalize())
        return queryset

    def get_paginated_response(self, data):
        return Response(data)


class FirstLessonCreate(CreateAPIView):
    serializer_class = LeadSerializer
    queryset = Lid.objects.all()
    permission_classes = [IsAuthenticated]


class ExportLeadToExcelAPIView(APIView):
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "start_date",
                openapi.IN_QUERY,
                description="Filter by start date (YYYY-MM-DD)",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "end_date",
                openapi.IN_QUERY,
                description="Filter by end date (YYYY-MM-DD)",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "is_student",
                openapi.IN_QUERY,
                description="Filter by whether the lead is a student (true/false)",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "filial_id",
                openapi.IN_QUERY,
                description="Filter by filial ID",
                type=openapi.TYPE_INTEGER,
            ),
            openapi.Parameter(
                "lid_stage_type",
                openapi.IN_QUERY,
                description="Filter by lid stage type",
                type=openapi.TYPE_STRING,
            ),
        ],
        responses={200: "Excel file generated"},
    )
    def get(self, request):
        # Get filters from query parameters
        start_date_str = request.GET.get("start_date")
        end_date_str = request.GET.get("end_date")

        lid_stage_type = request.GET.get("lid_stage_type")
        filial = self.request.GET.get("filial")
        is_archived = self.request.GET.get("is_archived")
        course_id = self.request.GET.get("course")
        call_operator_id = self.request.GET.get("call_operator")
        service_manager = self.request.GET.get("service_manager")
        sales_manager = self.request.GET.get("sales_manager")
        teacher = self.request.GET.get("teacher")
        channel = self.request.GET.get("marketing_channel")
        subject = self.request.GET.get("subject")
        is_student = self.request.GET.get("is_student")

        filter = {}
        if filial:
            filter["filial__id"] = filial
        if is_archived:
            filter["is_archived"] = is_archived.capitalize()
        if course_id:
            filter["groups__course__id"] = course_id
        if call_operator_id:
            filter["call_operator__id"] = call_operator_id
        if service_manager:
            filter["service_manager__id"] = service_manager
        if sales_manager:
            filter["sales_manager__id"] = sales_manager
        if teacher:
            filter["groups__teacher__id"] = teacher
        if channel:
            filter["marketing_channel__id"] = channel
        if subject:
            filter["subject__id"] = subject
        if is_student:
            filter["is_student"] = is_student.capitalize()

        queryset = Lid.objects.filter(**filter)

        date_format = "%Y-%m-%d"

        if start_date_str and end_date_str:
            start_date = datetime.strptime(start_date_str, date_format)
            end_date = datetime.strptime(end_date_str, date_format)
            start_datetime = datetime.combine(start_date, datetime.min.time())
            end_datetime = datetime.combine(end_date, datetime.max.time())
            queryset = queryset.filter(created_at__range=(start_datetime, end_datetime))

        elif start_date_str:
            start_date = datetime.strptime(start_date_str, date_format)
            start_datetime = datetime.combine(start_date, datetime.min.time())
            end_datetime = datetime.combine(start_date, datetime.max.time())
            queryset = queryset.filter(created_at__range=(start_datetime, end_datetime))

        if lid_stage_type:
            queryset = queryset.filter(lid_stage_type=lid_stage_type)

        # Create Excel workbook
        workbook = Workbook()
        sheet = workbook.active
        sheet.title = "Lids Data"

        # Define headers
        headers = [
            "Ism",
            "Familiya",
            "Telefon raqami",
            "Tug'ulgan sanasi",
            "O'quv tili",
            "O'quv sinfi",
            "Fan",
            "Ball",
            "Filial",
            "Marketing kanali",
            "Lead varonkasi",
            "Lead etapi",
            "Buyurtma etapi",
            "Arxivlangan",
            "Call Operator",
            "Sotuv menejeri",
            "O'quvchi bo'lgan",
            "Service manager",
            "Yaratilgan vaqti",
        ]
        sheet.append(headers)

        ORDERED_STAGE_LABELS = {
            "KUTULMOQDA": "Jarayonda",
            "BIRINCHI_DARSGA_KELMAGAN": "Sinov darsiga kelmagan",
            "BIRINCHI_DARS_BELGILANGAN": "Sinov darsi belgilangan",
            "YANGI_BUYURTMA": "Yangi buyurtma",
        }
        Lid_STAGE_LABELS = {
            "YANGI_LEAD": "Yangi lead",
            "KUTULMOQDA": "Jarayonda",
        }
        for lid in queryset:
            sheet.append(
                [
                    lid.first_name,
                    lid.last_name,
                    lid.phone_number,
                    lid.date_of_birth.strftime("%d-%m-%Y") if lid.date_of_birth else "",
                    (
                        "Uzbek tili"
                        if lid.education_lang == "UZB"
                        else (
                            "Ingliz tili"
                            if lid.education_lang == "ENG"
                            else "Rus tili" if lid.education_lang == "RU" else ""
                        )
                    ),
                    (
                        "Maktab"
                        if lid.edu_class == "SCHOOL"
                        else (
                            "Universitet"
                            if lid.edu_class == "UNIVERSITY"
                            else "Abutirent" if lid.edu_class else ""
                        )
                    ),
                    lid.subject.name if lid.subject else "",
                    lid.ball,
                    lid.filial.name if lid.filial else "",
                    lid.marketing_channel.name if lid.marketing_channel else "",
                    (
                        "Buyurtma yaratilgan"
                        if lid.lid_stage_type == "ORDERED_LID"
                        else "Yangi lead"
                    ),
                    Lid_STAGE_LABELS.get(lid.lid_stages, ""),
                    ORDERED_STAGE_LABELS.get(lid.ordered_stages, ""),
                    "Ha" if lid.is_archived else "Yo'q",
                    lid.call_operator.full_name if lid.call_operator else "",
                    lid.sales_manager.full_name if lid.sales_manager else "",
                    "Ha" if lid.is_student else "Yo'q",
                    lid.service_manager.full_name if lid.service_manager else "",
                    (
                        lid.created_at.strftime("%d-%m-%Y %H:%M:%S")
                        if lid.created_at
                        else ""
                    ),
                ]
            )

        # Style headers
        for col_num, header in enumerate(headers, 1):
            cell = sheet.cell(row=1, column=col_num)
            cell.font = Font(bold=True, size=12)
            cell.alignment = Alignment(horizontal="center", vertical="center")
            sheet.column_dimensions[cell.column_letter].width = 20

        # Create the HTTP response with the Excel file
        response = HttpResponse(
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        response["Content-Disposition"] = 'attachment; filename="Lids_Data.xlsx"'
        workbook.save(response)

        return response


class LeadStatisticsView(ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Lid.objects.all()

    def list(self, request, *args, **kwargs):
        user = request.user
        queryset = Lid.objects.all()

        filial = self.request.GET.get("filial")
        # is_archived = True
        # course_id = self.request.GET.get("course")
        call_operator_id = self.request.GET.get("call_operator")
        service_manager = self.request.GET.get("service_manager")
        sales_manager = self.request.GET.get("sales_manager")
        # teacher = self.request.GET.get("teacher")
        # channel = self.request.GET.get("channel")
        # subject = self.request.GET.get("subject")
        # is_student = self.request.GET.get("is_student")
        marketing_channel = self.request.GET.get("marketing_channel")
        subject = self.request.GET.get("subject")

        filter = {}

        if subject:
            filter["subject_id"] = subject

        if filial:
            filter["filial_id"] = filial
            queryset = queryset.filter(filial_id=filial)

        # if is_archived:
        #     filter["is_archived"] = True

        # if course_id:
        #     filter["groups__course__id"] = course_id

        if call_operator_id:
            filter["call_operator_id"] = call_operator_id

        if service_manager:
            filter["service_manager_id"] = service_manager

        if sales_manager:
            filter["sales_manager_id"] = sales_manager

        if marketing_channel:
            filter["marketing_channel_id"] = marketing_channel

        # if teacher:
        #     filter["groups__teacher__id"] = teacher

        # if channel:
        #     filter["subject__id"] = subject

        # if is_student:
        #     filter["is_student"] = is_student.capitalize()

        start_date_str = request.GET.get("start_date")
        end_date_str = request.GET.get("end_date")

        date_format = "%Y-%m-%d"

        if start_date_str and end_date_str:
            start_date = datetime.strptime(start_date_str, date_format).date()
            end_date = datetime.strptime(end_date_str, date_format).date()

            start_datetime = datetime.combine(start_date, datetime.min.time())
            end_datetime = datetime.combine(end_date, datetime.min.time()) + timedelta(
                days=1
            )

            filter["created_at__gte"] = start_datetime
            filter["created_at__lt"] = end_datetime

        elif start_date_str:
            start_date = datetime.strptime(start_date_str, date_format).date()

            start_datetime = datetime.combine(start_date, datetime.min.time())
            end_datetime = start_datetime + timedelta(days=1)

            filter["created_at__gte"] = start_datetime
            filter["created_at__lt"] = end_datetime

        f_start_date = filter.get("created_at__gte")
        f_end_date = filter.get("created_at__lt")

        if user.role == "CALL_OPERATOR" or user.is_call_center:
            queryset = queryset.filter(
                Q(filial__in=user.filial.all()) | Q(filial__isnull=True),
                Q(call_operator=user) | Q(call_operator__isnull=True),
            )

        else:
            queryset = queryset.filter(
                Q(filial__in=user.filial.all()) | Q(filial__isnull=True)
            )

        leads_count = queryset.filter(
            lid_stage_type="NEW_LID", is_archived=False, **filter
        ).count()

        new_leads = queryset.filter(
            lid_stage_type="NEW_LID",
            lid_stages="YANGI_LEAD",
            is_archived=False,
            **filter,
        ).count()

        in_progress = queryset.filter(
            lid_stage_type="NEW_LID",
            is_archived=False,
            lid_stages="KUTULMOQDA",
            **filter,
        ).count()

        order_created = (
            queryset.filter(
                is_archived=False,
                lid_stage_type="ORDERED_LID",
                ordered_date__isnull=False,
                **filter,
            )
            .exclude(call_operator__isnull=True)
            .count()
        )

        archived_new_leads = queryset.filter(
            is_archived=True, lid_stage_type="NEW_LID", **filter
        ).count()

        ordered_new = queryset.filter(
            lid_stage_type="ORDERED_LID",
            is_archived=False,
            ordered_stages="YANGI_BUYURTMA",
            **filter,
        ).count()

        ordered_new_fix = queryset.filter(
            ordered_date__isnull=False,
            ordered_stages="YANGI_BUYURTMA",
            is_archived=False,
            **filter,
        ).count()

        ordered_leads_count = (
            queryset.filter(lid_stage_type="ORDERED_LID", is_archived=False, **filter)
            .exclude(ordered_stages="BIRINCHI_DARS_BELGILANGAN")
            .count()
        )

        ordered_waiting_leads = queryset.filter(
            lid_stage_type="ORDERED_LID",
            is_archived=False,
            ordered_stages="KUTULMOQDA",
            **filter,
        ).count()

        ordered_archived = Archived.objects.filter(
            Q(lid__filial_id=filial) if filial else Q(),
            Q(created_at__gte=f_start_date) if f_start_date != None else Q(),
            Q(created_at__lt=f_end_date) if f_end_date != None else Q(),
            lid__isnull=False,
            is_archived=True,
            lid__lid_stage_type="ORDERED_LID",
        ).count()

        print(filter)

        first_lesson = queryset.filter(
            # Q(lid__filial_id=filial) if filial else Q(),
            # Q(created_at__gte=f_start_date) if f_start_date != None else Q(),
            # Q(created_at__lt=f_end_date) if f_end_date != None else Q(),
            lid_stage_type="ORDERED_LID",
            is_archived=False,
            ordered_stages="BIRINCHI_DARS_BELGILANGAN",
            is_student=False,
            **filter,
        ).count()

        first_lesson_not = queryset.filter(
            lid_stage_type="ORDERED_LID",
            is_archived=False,
            ordered_stages="BIRINCHI_DARSGA_KELMAGAN",
            **filter,
        ).count()

        all_archived = queryset.filter(
            is_archived=True,
            is_student=False,
            **filter,
        ).count()

        archived_lid = Archived.objects.filter(
            (
                (Q(lid__filial_id=filial) | Q(student__filial_id=filial))
                if filial
                else Q()
            ),
            lid__lid_stage_type="NEW_LID",
            lid__isnull=False,
            is_archived=True,
        ).count()

        first_lesson_all = FirstLLesson.objects.filter(
            Q(lid__filial_id=filial) if filial else Q(),
            Q(created_at__gte=f_start_date) if f_start_date != None else Q(),
            Q(created_at__lt=f_end_date) if f_end_date != None else Q(),
            lid__lid_stage_type="ORDERED_LID",
            lid__is_archived=False,
        ).count()

        # if filter.get("created_at__gte") is not None:
        #     first_lesson_all = first_lesson_all.filter(
        #         created_at__gte=filter["created_at__gte"]
        #     )

        # if filter.get("created_at__lt") is not None:
        #     first_lesson_all = first_lesson_all.filter(
        #         created_at__lt=filter["created_at__lt"]
        #     )

        new_student = Archived.objects.filter(
            # Make filter my lid_filial_id and created_at optional,
            # without any branching
            Q(student__filial_id=filial) if filial else Q(),
            Q(created_at__gte=f_start_date) if f_start_date != None else Q(),
            Q(created_at__lt=f_end_date) if f_end_date != None else Q(),
            is_archived=True,
            student__isnull=False,
            student__student_stage_type="NEW_STUDENT",
        ).count()

        active_student = Archived.objects.filter(
            Q(student__filial_id=filial) if filial else Q(),
            Q(created_at__gte=f_start_date) if f_start_date != None else Q(),
            Q(created_at__lt=f_end_date) if f_end_date != None else Q(),
            is_archived=True,
            student__isnull=False,
            student__student_stage_type="ACTIVE_STUDENT",
        ).count()

        no_debt = Archived.objects.filter(
            (
                Q(student__filial_id=filial) | Q(lid__filial_id=filial)
                if filial
                else Q()
            ),
            Q(created_at__gte=f_start_date) if f_start_date != None else Q(),
            Q(created_at__lt=f_end_date) if f_end_date != None else Q(),
            Q(
                student__balance__gte=100000,
            )
            | Q(
                lid__balance__gte=100000,
            ),
            is_archived=True,
        ).count()

        # lead_no_debt = Archived.objects.filter(
        #     Q(lid__filial_id=filial) if filial else Q(),
        #     Q(created_at__gte=f_start_date) if f_start_date != None else Q(),
        #     Q(created_at__lt=f_end_date) if f_end_date != None else Q(),
        #     is_archived=True,
        #     lid__isnull=False,
        #     lid__is_student=False,
        #     lid__balance__isnull=False,
        #     lid__balance__gte=100000,
        # ).count()

        debt_count = Archived.objects.filter(
            (
                Q(student__filial_id=filial) | Q(lid__filial_id=filial)
                if filial
                else Q()
            ),
            Q(created_at__gte=f_start_date) if f_start_date != None else Q(),
            Q(created_at__lt=f_end_date) if f_end_date != None else Q(),
            Q(
                student__balance__lt=100000,
            )
            | Q(lid__balance__lt=100000),
            is_archived=True,
        ).count()

        # lead_debt = Archived.objects.filter(
        #     Q(lid__filial_id=filial) if filial else Q(),
        #     Q(created_at__gte=f_start_date) if f_start_date != None else Q(),
        #     Q(created_at__lt=f_end_date) if f_end_date != None else Q(),
        #     is_archived=True,
        # ).count()

        no_debt_sum = (
            Archived.objects.filter(
                (
                    Q(student__filial_id=filial) | Q(lid__filial_id=filial)
                    if filial
                    else Q()
                ),
                Q(created_at__gte=f_start_date) if f_start_date != None else Q(),
                Q(created_at__lt=f_end_date) if f_end_date != None else Q(),
                Q(student__balance__gte=100000) | Q(lid__balance__gte=100000),
                is_archived=True,
            ).aggregate(
                total=Sum(
                    # "student__balance"
                    Coalesce(F("student__balance"), Value(0))
                    + Coalesce(F("lid__balance"), Value(0)),
                    output_field=FloatField(),
                )
            )[
                "total"
            ]
            or 0
        )

        # lead_no_debt_sum = (
        #     Archived.objects.filter(
        #         Q(lid__filial_id=filial) if filial else Q(),
        #         Q(created_at__gte=f_start_date) if f_start_date != None else Q(),
        #         Q(created_at__lt=f_end_date) if f_end_date != None else Q(),
        #         is_archived=True,
        #         lid__isnull=False,
        #         lid__is_student=False,
        #         lid__balance__isnull=False,
        #         lid__balance__gte=100000,
        #     ).aggregate(total=Sum("lid__balance"))["total"]
        #     or 0
        # )

        debt_sum = (
            Archived.objects.filter(
                (
                    Q(student__filial_id=filial) | Q(lid__filial_id=filial)
                    if filial
                    else Q()
                ),
                Q(created_at__gte=f_start_date) if f_start_date != None else Q(),
                Q(created_at__lt=f_end_date) if f_end_date != None else Q(),
                Q(student__balance__lt=100000) | Q(lid__balance__lt=100000),
                is_archived=True,
            ).aggregate(
                total=Sum(
                    # "student__balance"
                    Coalesce(F("student__balance"), Value(0))
                    + Coalesce(F("lid__balance"), Value(0)),
                    output_field=FloatField(),
                )
            )[
                "total"
            ]
            or 0
        )

        # lead_debt_sum = (
        #     Archived.objects.filter(
        #         Q(lid__filial_id=filial) if filial else Q(),
        #         Q(created_at__gte=f_start_date) if f_start_date != None else Q(),
        #         Q(created_at__lt=f_end_date) if f_end_date != None else Q(),
        #         is_archived=True,
        #         lid__isnull=False,
        #         lid__is_student=False,
        #         lid__balance__lt=100000,
        #     ).aggregate(total=Sum("lid__balance"))["total"]
        #     or 0
        # )

        response_data = {
            "new_lid_statistics": {
                "leads_count": leads_count,
                "new_leads": new_leads,
                "in_progress": in_progress,
                "order_created": order_created,
                "archived_new_leads": archived_new_leads,
            },
            "ordered_statistics": {
                "ordered_leads_count": ordered_leads_count,
                "ordered_new": ordered_new,
                "ordered_new_fix": ordered_new_fix,
                "ordered_waiting_leads": ordered_waiting_leads,
                "ordered_first_lesson_not_come": first_lesson_not,
                "ordered_first_lesson": first_lesson,
                "ordered_archived": ordered_archived,
                "first_lesson_all": first_lesson_all,
            },
            "lid_archived": {
                "all": all_archived,
                "lid": archived_lid,
                "order": ordered_archived,
            },
            "student_archived": {
                "all": all_archived + new_student + active_student,
                "new_students": new_student,
                "active_students": active_student,
                "no-debt": no_debt,
                # + lead_no_debt,
                "debt": debt_count,
                # + lead_debt,
                "no_debt_sum": no_debt_sum,
                # + lead_no_debt_sum,
                "debt_sum": debt_sum,
                # + lead_debt_sum,
            },
        }

        return Response(response_data)


class BulkUpdate(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        data = request.data.get("lids", [])

        if not data:
            raise ValidationError("No lids data provided.")

        serializer = LeadSerializer()

        try:
            updated_lids = serializer.update_bulk_lids(data)
            return Response(
                {"message": "Bulk update successful.", "updated_lids": updated_lids},
                status=status.HTTP_200_OK,
            )
        except ValidationError as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class LeadStatistics(ListAPIView):
    serializer_class = LeadSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]

    search_fields = [
        "first_name",
        "last_name",
        "phone_number",
    ]
    filterset_fields = [
        "student_type",
        "education_lang",
        "filial",
        "marketing_channel",
        "lid_stage_type",
        "lid_stages",
        "ordered_stages",
        "is_double",
        "is_archived",
    ]

    def get_queryset(self):
        user = self.request.user

        if user.is_anonymous:
            return Lid.objects.none()

        queryset = Lid.objects.all()
        filial = self.request.GET.get("filial")

        if user.role == "CALL_OPERATOR" or user.is_call_center:
            queryset = queryset.filter(
                Q(filial__in=user.filial.all()) | Q(filial__isnull=True),
                Q(call_operator=user) | Q(call_operator__isnull=True),
            )
        else:
            queryset = queryset.filter(Q(filial_id=filial) | Q(filial__isnull=True))

        is_archived = self.request.GET.get("is_archived")
        search_term = self.request.GET.get("search", "")
        course_id = self.request.GET.get("course")
        call_operator_id = self.request.GET.get("call_operator")
        service_manager = self.request.GET.get("service_manager")
        sales_manager = self.request.GET.get("sales_manager")
        teacher = self.request.GET.get("teacher")
        channel = self.request.GET.get("channel")
        subject = self.request.GET.get("subject")
        is_student = self.request.GET.get("is_student")

        if is_archived == "True":
            queryset = queryset.filter(is_archived=True)

        if channel:
            queryset = queryset.filter(marketing_channel__id=channel)

        if service_manager:
            queryset = queryset.filter(service_manager_id=service_manager)

        if sales_manager:
            queryset = queryset.filter(sales_manager_id=sales_manager)

        if teacher:
            queryset = queryset.filter(groups__group__teacher_id=teacher)

        if subject:
            queryset = queryset.filter(subject_id=subject)

        if is_student == "false":
            queryset = queryset.filter(is_student=False)

        if call_operator_id:
            queryset = queryset.filter(call_operator_id=call_operator_id)

        if course_id:
            queryset = queryset.filter(groups__group__course_id=course_id)

        if search_term:
            try:
                queryset = queryset.filter(
                    Q(first_name__icontains=search_term)
                    | Q(last_name__icontains=search_term)
                    | Q(phone_number__icontains=search_term)
                )
            except FieldError as e:
                print(f"FieldError: {e}")

        # ✅ Date Filtering
        start_date = self.request.GET.get("start_date")
        end_date = self.request.GET.get("end_date")

        if start_date and end_date:
            queryset = queryset.filter(
                created_at__gte=start_date, created_at__lte=end_date
            )
        elif start_date:
            try:
                start_date = parse_datetime(start_date).date()
                queryset = queryset.filter(created_at__gte=start_date)
            except ValueError:
                pass
        elif end_date:
            try:
                end_date = parse_datetime(end_date).date()
                queryset = queryset.filter(created_at__lte=end_date)
            except ValueError:
                pass

        return queryset


class LeadArchiveAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request: HttpRequest, *args, **kwargs):
        serializer = LeadArchiveSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            lead = Lid.objects.select_for_update().filter(id=self.kwargs["pk"]).first()
            if lead is None:
                raise NotFound("Lead topilmadi")

            if not lead.is_archived:
                lead.is_archived = True
                lead.set_archived_at()

                lead.save(update_fields=["is_archived", "archived_at"])

                archived_first_lessons = lead.first_lessons.filter(
                    is_archived=False
                ).update(is_archived=True, archived_at=timezone.now())

                Archive.objects.create(
                    lead=lead,
                    reason=serializer.validated_data["comment"],
                    creator=request.user,
                )

                if lead.ordered_stages == "BIRINCHI_DARS_BELGILANGAN":
                    if (
                        lead.sales_manager
                        and lead.sales_manager.f_sm_fine_firstlesson_archived > 0
                    ):
                        lead.sales_manager.transactions.create(
                            reason="FINE_FOR_ARCHIVED_FIRST_LESSON",
                            lead=lead,
                            amount=lead.sales_manager.f_sm_fine_firstlesson_archived,
                            comment=f"Sinov darsi etapidagi lead arxivlagani uchun jarima: {lead.first_name} {lead.last_name} {lead.middle_name}",
                        )

        return Response({"ok": True})


class LeadCreateOrderAPIView(UpdateAPIView):

    queryset = Lid.objects.filter()

    serializer_class = LeadSerializer

    def perform_update(self, serializer: LeadSerializer):

        instance: Lid = serializer.save(
            lid_stage_type="ORDERED_LID", ordered_stages="YANGI_BUYURTMA"
        )

        if (
            instance.call_operator
            and instance.call_operator.f_op_bonus_create_order > 0
        ):

            instance.call_operator.transactions.create(
                reason="BONUS",
                lead=instance,
                amount=instance.call_operator.f_op_bonus_create_order,
                comment=f"Yangi buyurtma yaratgani uchun bonus. Buyurtma: {instance.first_name} {instance.last_name}",
            )

        return super().perform_update(serializer)
