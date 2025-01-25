from django.core.exceptions import FieldError
from django.db.models import Q
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.generics import RetrieveUpdateDestroyAPIView, ListAPIView, \
    ListCreateAPIView, CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from translate import Translator
from .models import Lid
from .tests import CustomPagination
from ..new_lid.serializers import LidSerializer
from ...account.permission import FilialRestrictedQuerySetMixin




class LidListCreateView(FilialRestrictedQuerySetMixin,ListCreateAPIView):
    serializer_class = LidSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination

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
    ]

    def get_queryset(self):
        user = self.request.user
        if user.is_anonymous:
            return Lid.objects.none()

        # Base queryset
        queryset = Lid.objects.filter(is_archived=False)

        # Role-based filtering
        if user.role == "CALL_OPERATOR":
            queryset = queryset.filter(
                Q(call_operator=user) |
                Q(call_operator=None, filial=None)
            )
        if user.role == "ADMINISTRATOR":
            queryset = queryset.filter(filial=user.filial)

        # Debugging search_term
        search_term = self.request.query_params.get("search", "")
        print("Search term:", search_term)

        # Apply search logic only if search_term exists
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

        if start_date:
            queryset = queryset.filter(created_at__gte=start_date)
        if end_date:
            queryset = queryset.filter(created_at__lte=end_date)

        return queryset


class LidRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    serializer_class = LidSerializer
    queryset = Lid.objects.all()
    permission_classes = [IsAuthenticated]


class LidListNoPG(FilialRestrictedQuerySetMixin,ListAPIView):
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
            openapi.Parameter("start_date", openapi.IN_QUERY, description="Filter by start date (YYYY-MM-DD)", type=openapi.TYPE_STRING),
            openapi.Parameter("end_date", openapi.IN_QUERY, description="Filter by end date (YYYY-MM-DD)", type=openapi.TYPE_STRING),
            openapi.Parameter("is_student", openapi.IN_QUERY, description="Filter by whether the lead is a student (true/false)", type=openapi.TYPE_STRING),
            openapi.Parameter("filial_id", openapi.IN_QUERY, description="Filter by filial ID", type=openapi.TYPE_INTEGER),
            openapi.Parameter("lid_stage_type",openapi.IN_QUERY, description="Filter by lid stage type", type=openapi.TYPE_STRING),
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
        queryset = Lid.objects.all()

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
            "Tug'ulgan sanasi", "O'quv tili","O'quv sinfi",
            "Fan", "Ball", "Filial", "Marketing kanali", "Lead varonkasi",
            "Lead etapi", "Buyurtma etapi", "Arxivlangan",
            "Call Operator", "O'quvchi bo'lgan", "Moderator", "Yaratilgan vaqti"
        ]
        sheet.append(headers)

        # Populate Excel rows
        for lid in queryset:
            sheet.append([
                lid.first_name,
                lid.last_name,
                lid.phone_number,
                lid.date_of_birth.strftime('%d-%m-%Y') if lid.date_of_birth else "",
                lid.education_lang,
                lid.edu_class,
                lid.subject,
                lid.ball,
                lid.filial.name if lid.filial else "",
                lid.marketing_channel.name if lid.marketing_channel else "",
                lid.lid_stage_type,
                lid.lid_stages if lid.lid_stages else "",
                lid.ordered_stages if lid.ordered_stages else "",
                "Ha" if lid.is_archived else "Yo'q",
                lid.call_operator.full_name if lid.call_operator else "",
                "Ha" if lid.is_student else "Yo'q",
                lid.moderator.full_name if lid.moderator else "",
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



