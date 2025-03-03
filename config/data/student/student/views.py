from django.db.models import Sum
from django.http import HttpResponse
from django.utils.dateparse import parse_datetime
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
from ...finances.finance.models import Finance


class StudentListView(FilialRestrictedQuerySetMixin, ListCreateAPIView):
    queryset = Student.objects.all().select_related('marketing_channel', 'sales_manager', 'service_manager')
    serializer_class = StudentSerializer
    permission_classes = [IsAuthenticated]

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ["first_name", "last_name", "phone"]
    filterset_fields = [
        "student_type",
        "education_lang",
        "marketing_channel",
        "student_stage_type",
        "balance_status",
        "is_archived",
        "sales_manager",  # Added sales_manager filter
        "call_operator",  # Added call_operator filter
        # "course",  # Added courses filter
    ]

    def get_queryset(self):
        """
        Customize queryset filtering based on user roles and other criteria.
        """
        user = self.request.user

        queryset = self.queryset.filter(filial=user.filial.first())

        # Additional role-based filtering
        if hasattr(user, "role"):
            if user.role == "CALL_OPERATOR":
                queryset = queryset.none()
            elif user.role == "ADMINISTRATOR":
                queryset = queryset.filter(filial=user.filial.all())

        # Add filters based on query parameters (for sales manager and operators)
        sales_manager_id = self.request.query_params.get('sales_manager')
        call_operator_id = self.request.query_params.get('call_operator')
        from_price = self.request.query_params.get('from_price')
        edu_langauge = self.request.query_params.get('edu_langauge')
        to_price = self.request.query_params.get('to_price')
        course_id = self.request.query_params.get('course')
        service_manager = self.request.query_params.get('service_manager')
        group_id = self.request.query_params.get("group")
        subject_id = self.request.query_params.get("subject")


        if from_price:
            queryset = queryset.filter(balance__gte=from_price)
        if to_price:
            queryset = queryset.filter(balance__lte=to_price)
        if from_price and to_price:
            queryset = queryset.filter(balance__gte=from_price, balance__lte=to_price)

        if edu_langauge:
            queryset = queryset.filter(education_lang=edu_langauge)

        if subject_id:
            queryset = queryset.filter(subject__id=subject_id)

        if sales_manager_id:
            queryset = queryset.filter(sales_manager__id=sales_manager_id)
        if call_operator_id:
            queryset = queryset.filter(call_operator__id=call_operator_id)

        if course_id:
            queryset = queryset.filter(
                students_group__group__course__id=course_id)  # Assuming Many-to-Many relation in groups
        if service_manager:
            queryset = queryset.filter(service_manager__id=service_manager)

        if group_id:
            queryset = queryset.filter(students_group__group__id=group_id)

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


class StudentListNoPG(FilialRestrictedQuerySetMixin, ListAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [IsAuthenticated]

    def get_paginated_response(self, data):
        return Response(data)


class StudentScheduleView(FilialRestrictedQuerySetMixin, ListAPIView):
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        student_groups = StudentGroup.objects.filter(student_id=self.kwargs['pk']).values_list('group_id', flat=True)
        return Lesson.objects.filter(group_id__in=student_groups).order_by("day", "start_time")


class StudentStatistics(FilialRestrictedQuerySetMixin, ListAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # Calculate statistics
        if request.user.role != "CALL_OPERATOR":
            user = request.user  # Set 'user' to the actual user object
        else:
            user = None

        if user:
            filial = user.filial.all()  # Get the filial of the authenticated user
        else:
            filial = None  # Handle the case where user is None (e.g., for CALL_OPERATOR)

        new_students_count = Student.objects.filter(is_archived=False, filial__in=filial,
                                                    student_stage_type="NEW_STUDENT").count()
        total_debt = \
            Student.objects.filter(is_archived=False, filial__in=filial, student_stage_type="NEW_STUDENT",
                                   balance__lt=0).aggregate(total_debt=Sum('balance'))['total_debt'] or 0
        archived_new_students = Student.objects.filter(is_archived=True, filial__in=filial,
                                                       student_stage_type="NEW_STUDENT").count()

        # Ordered statistics
        student_count = Student.objects.filter(is_archived=False, filial__in=filial,
                                               student_stage_type="ACTIVE_STUDENT").count()
        total_income = \
            Student.objects.filter(is_archived=False, filial__in=filial, student_stage_type="ACTIVE_STUDENT",
                                   balance__gt=0).aggregate(total_income=Sum('balance'))['total_income'] or 0
        student_total_debt = \
            Student.objects.filter(is_archived=False, filial__in=filial, student_stage_type="ACTIVE_STUDENT",
                                   balance__lt=0).aggregate(
                total_debt=Sum('balance'))['total_debt'] or 0

        archived_student = Student.objects.filter(is_archived=True, filial__in=filial,
                                                  student_stage_type="ACTIVE_STUDENT").count()

        from_new_to_active = Finance.objects.filter(
            student__isnull=False,
            student__student_stage_type="ACTIVE_STUDENT",
            attendance__isnull=False,
            is_first=True,
            filial__in=filial,
        ).count()

        almost_debt = Student.objects.filter(is_archived=False, filial__in=filial,balance__gte=0,
                                             balance__lte=100000).count()

        statistics = {
            "new_students_count": new_students_count,
            "new_to_active": from_new_to_active,
            "new_students_total_debt": total_debt,
            "archived_new_students": archived_new_students,
        }

        # Additional ordered statistics (could be pagination or other stats)
        ordered_statistics = {
            "student_count": student_count,
            "almost_debt": almost_debt,
            "total_income": total_income,  # Serialized data
            "student_total_debt": student_total_debt,
            "archived_student": archived_student,
        }

        # Including both statistics and ordered data in the response
        response_data = {
            "statistics": statistics,
            "ordered_statistics": ordered_statistics,
        }

        return Response(response_data)


class StudentAllStatistics(FilialRestrictedQuerySetMixin, ListAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):

        filter = {}
        filial = self.request.query_params.get('filial')
        if filial:
            filter["filial"] = filial

        all_students = Student.objects.filter(is_archived=False, **filter
                                              ).count()
        archived_students = Student.objects.filter(is_archived=True, **filter).count()
        if StudentGroup.student:
            course_ended = StudentGroup.objects.filter(
                group__status="INACTIVE"
            ).count()
        else:
            course_ended = StudentGroup.objects.filter(
                group__status="INACTIVE",
            ).count()
        balance_active = Student.objects.filter(is_archived=False, **filter,
                                                balance_status="ACTIVE",
                                                ).count()
        balance_inactive = Student.objects.filter(
            is_archived=False, **filter, balance_status="INACTIVE"
        ).count()
        response_data = {
            "all_students": all_students,
            "archived_students": archived_students,
            "course_ended": course_ended,
            "balance_active": balance_active,
            "balance_inactive": balance_inactive,
        }
        return Response(response_data)


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
            openapi.Parameter("student_stage_type", openapi.IN_QUERY, description="Filter by student stage type",
                              type=openapi.TYPE_STRING),
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
            "Balansi", "Balans statusi", "Arxivlangan",
            "Call Operator", "Service manager", "Yaratilgan vaqti"
        ]
        sheet.append(headers)

        # Loop through students and append data
        for student in queryset:
            # Retrieve the learning subjects if the group is active
            # subjects = self.get_student_subjects(student)

            for student in queryset:
                sheet.append([
                    student.first_name,
                    student.last_name,
                    student.phone,
                    student.date_of_birth.strftime('%d-%m-%Y') if student.date_of_birth else "",
                    "Uzbek tili" if student.education_lang == "UZB" else "Ingliz tili" if student.education_lang == "ENG" else "Rus tili" if student.education_lang == "RU" else "",
                    "Maktab" if student.edu_class == "SCHOOL" else "Universitet" if student.edu_class == "UNIVERSITY" else "",
                    student.subject.name if student.subject else "",
                    student.ball,
                    ", ".join([filial.name for filial in student.filial.all()]) if student.filial.exists() else "",
                    student.marketing_channel.name if student.marketing_channel else "",
                    "Yangi student" if student.student_stage_type == "NEW_STUDENT" else "Faol student",
                    student.balance_status if student.balance_status else "",
                    student.balance if student.balance else "",
                    "Ha" if student.is_archived else "Yo'q",
                    student.call_operator.full_name if student.call_operator else "",
                    student.service_manager.full_name if student.service_manager else "",
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
