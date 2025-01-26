from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font
from rest_framework import status
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import ListCreateAPIView, ListAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Student
from .serializers import StudentSerializer, StudentTokenObtainPairSerializer
from ..lesson.models import Lesson
from ..lesson.serializers import LessonSerializer
from ..studentgroup.models import StudentGroup
from ...account.permission import FilialRestrictedQuerySetMixin


class StudentListView(FilialRestrictedQuerySetMixin, ListCreateAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [IsAuthenticated]

    filter_backends = (DjangoFilterBackend, OrderingFilter, SearchFilter)

    search_fields = ('first_name', 'last_name', 'phone')

    ordering_fields = ('student_stage_type', 'is_archived', 'moderator',
                                                            'marketing_channel', 'filial')

    filterset_fields = ('student_stage_type', 'is_archived',
                        'moderator', 'marketing_channel', 'filial')

    def get_queryset(self):
        """
        Customize queryset filtering based on user roles and other criteria.
        """
        user = self.request.user

        queryset = super().get_queryset()

        # Additional role-based filtering
        if hasattr(user, "role"):
            if user.role == "CALL_OPERATOR":
                queryset = queryset.none()
            elif user.role == "ADMINISTRATOR":
                queryset = queryset.filter(filial=user.filial)

        return queryset





class StudentLoginAPIView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = StudentTokenObtainPairSerializer(data=request.data)

        if serializer.is_valid():
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class StudentDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [IsAuthenticated]

class StudentListNoPG(FilialRestrictedQuerySetMixin,ListAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [IsAuthenticated]

    def get_paginated_response(self, data):
        return Response(data)



class StudentScheduleView(FilialRestrictedQuerySetMixin,ListAPIView):
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        student_groups = StudentGroup.objects.filter(student_id=self.kwargs['pk']).values_list('group_id', flat=True)
        return Lesson.objects.filter(group_id__in=student_groups).order_by("day", "start_time")



class ExportLidToExcelAPIView(APIView):
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter("start_date", openapi.IN_QUERY, description="Filter by start date (YYYY-MM-DD)", type=openapi.TYPE_STRING),
            openapi.Parameter("end_date", openapi.IN_QUERY, description="Filter by end date (YYYY-MM-DD)", type=openapi.TYPE_STRING),
            openapi.Parameter("is_student", openapi.IN_QUERY, description="Filter by whether the lead is a student (true/false)", type=openapi.TYPE_STRING),
            openapi.Parameter("filial_id", openapi.IN_QUERY, description="Filter by filial ID", type=openapi.TYPE_INTEGER),
            openapi.Parameter("student_stage_type", openapi.IN_QUERY, description="Filter by student stage type", type=openapi.TYPE_STRING),
        ],
        responses={200: "Excel file generated"}
    )
    def get(self, request):
        # Get filters from query parameters
        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")
        filial_id = request.query_params.get("filial_id")
        student_stage_type = request.query_params.get("student_stage_type")

        # Filter queryset
        queryset = Student.objects.all()

        if start_date and end_date:
            queryset = queryset.filter(created_at__range=[start_date, end_date])
        if filial_id:
            queryset = queryset.filter(filial_id=filial_id)
        if student_stage_type:
            queryset = queryset.filter(student_stage_type=student_stage_type)

        # Create Excel workbook
        workbook = Workbook()
        sheet = workbook.active
        sheet.title = "Student Data"

        # Define headers
        headers = [
            "Ism", "Familiya", "Telefon raqami",
            "Tug'ulgan sanasi", "O'quv tili", "O'quv sinfi",
            "Fan", "Ball", "Filial", "Marketing kanali", "O'quvchi varonkasi",
            "Balansi","Balans statusi", "Arxivlangan",
            "Call Operator", "Moderator", "Yaratilgan vaqti"
        ]
        sheet.append(headers)

        # Loop through students and append data
        for student in queryset:
            # Retrieve the learning subjects if the group is active
            # subjects = self.get_student_subjects(student)

            sheet.append([
                student.first_name,
                student.last_name,
                student.phone,
                student.date_of_birth.strftime('%d-%m-%Y') if student.date_of_birth else "",
                student.education_lang,
                student.edu_class,
                student.subject.name if student.subject else "",
                student.ball,
                student.filial.name if student.filial else "",
                student.marketing_channel.name if student.marketing_channel else "",
                student.student_stage_type,
                student.balance_status if student.balance_status else "",
                student.balance if student.balance else "",
                "Ha" if student.is_archived else "Yo'q",
                student.call_operator.full_name if student.call_operator else "",
                student.moderator.full_name if student.moderator else "",
                student.created_at.strftime('%d-%m-%Y %H:%M:%S') if student.created_at else "",
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

    # def get_student_subjects(self, student):
    #     # Check if the student has an active group
    #     active_group = StudentGroup.objects.filter(student=student, group__status="ACTIVE").first()
    #     if active_group:
    #         # Return the subjects associated with the active group
    #         return ', '.join([subject.name for subject in active_group.subjects.all()])
    #     return "No active group"
