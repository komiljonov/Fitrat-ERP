from django.core.exceptions import FieldError
from django.db.models import Q
from django.http import HttpResponse
from django.utils.dateparse import parse_datetime
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.generics import RetrieveUpdateDestroyAPIView, ListAPIView, \
    ListCreateAPIView, CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Lid
from .serializers import LidSerializer
from ...account.permission import FilialRestrictedQuerySetMixin


class LidListCreateView(ListCreateAPIView):
    serializer_class = LidSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]

    search_fields = ["first_name", "last_name", "phone_number", ]
    filterset_fields = [
        "student_type",
        "education_lang",
        "filial",
        "marketing_channel",
        "lid_stage_type",
        "lid_stages",
        "ordered_stages",
        "is_dubl",
        "is_archived",
    ]

    def get_queryset(self):
        user = self.request.user

        # Handle anonymous users
        if user.is_anonymous:
            return Lid.objects.none()

        if user.role == "DIRECTOR":
            return Lid.objects.all()

        # Start with a base queryset
        queryset = Lid.objects.all()

        # Dynamically filter by `is_archived` if provided
        # is_student = self.request.query_params.get("is_student")
        # if is_student:
        #     queryset = queryset.filter(is_student=is_student)
        is_archived = self.request.query_params.get("is_archived")
        if is_archived == "True":
            queryset = queryset.filter(is_archived=(is_archived.lower() == "true"))

        if user.role == "CALL_OPERATOR" or user.is_call_center == True:
            queryset = queryset.filter(
                Q(call_operator=user) | Q(call_operator__isnull=True),
                Q(filial__in=user.filial.all()) | Q(filial__isnull=True)
            )

        else:
            queryset = queryset.filter(Q(filial__in=user.filial.all()) | Q(filial__isnull=True))

        # Debugging search_term
        search_term = self.request.query_params.get("search", "")
        course_id = self.request.query_params.get('course')
        call_operator_id = self.request.query_params.get('call_operator')
        service_manager = self.request.query_params.get('service_manager')
        sales_manager = self.request.query_params.get('sales_manager')
        teacher = self.request.query_params.get('teacher')
        subject = self.request.query_params.get('subject')

        if service_manager:
            queryset = queryset.filter(service_manager__id=service_manager)

        if sales_manager:
            queryset = queryset.filter(sales_manager__id=sales_manager)

        if teacher:
            queryset = queryset.filter(teacher__id=teacher)

        if subject:
            queryset = queryset.filter(subject__id=subject)

        if call_operator_id:
            queryset = queryset.filter(call_operator__id=call_operator_id)

        if course_id:
            queryset = queryset.filter(lids_group__group__course__id=course_id)

        if search_term:
            try:
                queryset = queryset.filter(
                    Q(first_name__icontains=search_term) |
                    Q(last_name__icontains=search_term) |
                    Q(phone_number__icontains=search_term)
                )
            except FieldError as e:
                print(f"FieldError: {e}")

        # Apply start_date and end_date filters
        start_date = self.request.query_params.get("start_date")
        end_date = self.request.query_params.get("end_date")

        if start_date and end_date:
            queryset = queryset.filter(created_at__range=[start_date, end_date])
        elif start_date:
            try:
                start_date = parse_datetime(start_date).date()
                queryset = queryset.filter(created_at__date=start_date)
            except ValueError:
                pass  # Handle invalid date format, if necessary
        elif end_date:
            try:
                end_date = parse_datetime(end_date).date()
                queryset = queryset.filter(created_at__date=end_date)
            except ValueError:
                pass  # Handle invalid date format, if necessary

        return queryset


class LidRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    serializer_class = LidSerializer
    queryset = Lid.objects.all()
    permission_classes = [IsAuthenticated]


class LidListNoPG(ListAPIView):
    queryset = Lid.objects.all()
    serializer_class = LidSerializer

    def get_paginated_response(self, data):
        return Response(data)


class FirstLessonCreate(CreateAPIView):
    serializer_class = LidSerializer
    queryset = Lid.objects.all()
    permission_classes = [IsAuthenticated]


class ExportLidToExcelAPIView(APIView):
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter("start_date", openapi.IN_QUERY, description="Filter by start date (YYYY-MM-DD)",
                              type=openapi.TYPE_STRING),
            openapi.Parameter("end_date", openapi.IN_QUERY, description="Filter by end date (YYYY-MM-DD)",
                              type=openapi.TYPE_STRING),
            openapi.Parameter("is_student", openapi.IN_QUERY,
                              description="Filter by whether the lead is a student (true/false)",
                              type=openapi.TYPE_STRING),
            openapi.Parameter("filial_id", openapi.IN_QUERY, description="Filter by filial ID",
                              type=openapi.TYPE_INTEGER),
            openapi.Parameter("lid_stage_type", openapi.IN_QUERY, description="Filter by lid stage type",
                              type=openapi.TYPE_STRING),
        ],
        responses={200: "Excel file generated"}
    )
    def get(self, request):
        # Get filters from query parameters
        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")
        is_student = request.query_params.get("is_student")
        filial_id = request.query_params.get("filial_id")
        lid_stage_type = request.query_params.get("lid_stage_type")

        # Filter queryset
        queryset = Lid.objects.filter(lid_stage_type="ORDERED_LID")

        if start_date and end_date:
            queryset = queryset.filter(created_at__range=[start_date, end_date])
        if is_student is not None:
            queryset = queryset.filter(is_student=is_student.lower() == "true")
        if filial_id:
            queryset = queryset.filter(filial_id=filial_id)
        if lid_stage_type:
            queryset = queryset.filter(lid_stage_type=lid_stage_type)

        # Create Excel workbook
        workbook = Workbook()
        sheet = workbook.active
        sheet.title = "Lids Data"

        # Define headers
        headers = [
            "Ism", "Familiya", "Telefon raqami",
            "Tug'ulgan sanasi", "O'quv tili", "O'quv sinfi",
            "Fan", "Ball", "Filial", "Marketing kanali", "Lead varonkasi",
            "Lead etapi", "Buyurtma etapi", "Arxivlangan",
            "Call Operator", "O'quvchi bo'lgan", "Service manager", "Yaratilgan vaqti"
        ]
        sheet.append(headers)

        # Populate Excel rows
        for lid in queryset:
            sheet.append([
                lid.first_name,
                lid.last_name,
                lid.phone_number,
                lid.date_of_birth.strftime('%d-%m-%Y') if lid.date_of_birth else "",
                "Uzbek tili" if lid.education_lang == "UZB" else "Ingliz tili" if lid.education_lang == "ENG" else "Rus tili" if lid.education_lang == "RU" else "",
                "Maktab" if lid.edu_class == "SCHOOL" else "Universitet" if lid.edu_class == "UNIVERSITY" else "Abutirent" if lid.edu_class else "",
                lid.subject.name if lid.subject else "",
                lid.ball,
                ", ".join([filial.name for filial in lid.filial.all()]) if lid.filial.exists() else "",
                lid.marketing_channel.name if lid.marketing_channel else "",
                "Buyurtma yaratilgan" if lid.lid_stage_type == "ORDERED_LID" else "Yangi lead",
                lid.lid_stages if lid.lid_stages else "",
                lid.ordered_stages if lid.ordered_stages else "",
                "Ha" if lid.is_archived else "Yo'q",
                lid.call_operator.full_name if lid.call_operator else "",
                "Ha" if lid.is_student else "Yo'q",
                lid.service_manager.full_name if lid.service_manager else "",
                lid.created_at.strftime('%d-%m-%Y %H:%M:%S') if lid.created_at else "",
            ])

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


class LidStatisticsView(ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Lid.objects.all()

    def list(self, request, *args, **kwargs):
        user = request.user

        # Director sees everything
        if user.role == "DIRECTOR":
            queryset = Lid.objects.all()

        if user.role != "CALL_OPERATOR" and user.is_call_center:
            queryset = Lid.objects.filter(filial__in=user.filial.all())

        if user.role != "CALL OPERATOR" and user.is_call_center == False:
            queryset = Lid.objects.filter(filial__in=user.filial.all())

        # Special conditions for call operators
        if user.role == "CALL_OPERATOR" or user.is_call_center:
            queryset = Lid.objects.filter(
                Q(call_operator=user) | Q(call_operator__isnull=True),
                Q(filial__in=user.filial) | Q(filial__isnull=True)
            )

        # Common filters
        leads_count = queryset.filter(
            lid_stage_type="NEW_LID",
            is_archived=False
        ).count()

        new_leads = queryset.filter(
            lid_stage_type="NEW_LID",
            lid_stages="YANGI_LEAD",
            is_archived=False,
        ).count()

        in_progress = queryset.filter(
            lid_stage_type="NEW_LID",
            is_archived=False,
            lid_stages="KUTULMOQDA"
        ).count()

        order_created = queryset.filter(
            is_archived=False,
            lid_stage_type="ORDERED_LID"
        ).exclude(call_operator__isnull=True).count()

        archived_new_leads = queryset.filter(
            is_archived=True,
            lid_stage_type="NEW_LID"
        ).count()

        # Ordered Leads
        ordered_new = queryset.filter(
            lid_stage_type="ORDERED_LID",
            is_archived=False,
            ordered_stages="YANGI_BUYURTMA"
        ).count()

        ordered_leads_count = queryset.filter(
            lid_stage_type="ORDERED_LID",
            is_archived=False
        ).count()

        ordered_waiting_leads = queryset.filter(
            lid_stage_type="ORDERED_LID",
            is_archived=False,
            ordered_stages="KUTULMOQDA"
        ).count()

        ordered_archived = queryset.filter(
            is_archived=True,
            lid_stage_type="ORDERED_LID"
        ).count()

        first_lesson = queryset.filter(
            lid_stage_type="ORDERED_LID",
            is_archived=False,
            ordered_stages="BIRINCHI_DARS_BELGILANGAN"
        ).count()

        first_lesson_not = queryset.filter(
            lid_stage_type="ORDERED_LID",
            is_archived=False,
            ordered_stages="BIRINCHI_DARSGA_KELMAGAN"
        ).count()

        # Archived Leads
        all_archived = queryset.filter(is_archived=True, is_student=False).count()
        archived_lid = queryset.filter(lid_stage_type="NEW_LID", is_student=False, is_archived=True).count()
        archived_order = queryset.filter(lid_stage_type="ORDERED_LID", is_student=False, is_archived=True).count()

        # Compile statistics into response
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
                "ordered_waiting_leads": ordered_waiting_leads,
                "ordered_first_lesson_not_come": first_lesson_not,
                "ordered_first_lesson": first_lesson,
                "ordered_archived": ordered_archived,
            },
            "lid_archived": {
                "all": all_archived,
                "lid": archived_lid,
                "order": archived_order,
            },
        }

        return Response(response_data)


class BulkUpdate(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        data = request.data.get('lids', [])

        if not data:
            raise ValidationError("No lids data provided.")

        serializer = LidSerializer()

        try:
            updated_lids = serializer.update_bulk_lids(data)
            return Response({"message": "Bulk update successful.", "updated_lids": updated_lids},
                            status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
