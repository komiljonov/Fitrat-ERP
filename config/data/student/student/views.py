from datetime import datetime

from django.db.models import Sum, Count, Q, Case, When, Value, IntegerField
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils.dateparse import parse_datetime
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from icecream import ic
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import (
    ListCreateAPIView,
    ListAPIView,
    RetrieveUpdateDestroyAPIView,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from rest_framework.request import HttpRequest, Request

from rest_framework.exceptions import ValidationError

from django.db import transaction

from data.student.student.filters import StudentFilter

from .models import Student
from .serializers import StudentSerializer
from data.student.lesson.models import FirstLLesson
from data.student.lesson.serializers import FirstLessonSerializer
from data.student.studentgroup.models import StudentGroup
from data.account.permission import FilialRestrictedQuerySetMixin
from data.finances.finance.models import Finance
from data.lid.new_lid.models import Lid
from data.lid.new_lid.views import CustomPagination


class StudentListView(FilialRestrictedQuerySetMixin, ListCreateAPIView):
    today = datetime.today()
    queryset = (
        Student.objects.all()
        .select_related("marketing_channel", "sales_manager", "service_manager")
        .annotate(
            check_is_frozen=Case(
                When(
                    frozen_from_date__lte=today,
                    frozen_till_date__gte=today,
                    then=Value(1),
                ),
                default=Value(0),
                output_field=IntegerField(),
            )
        )
    )

    serializer_class = StudentSerializer
    pagination_class = CustomPagination

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ["first_name", "last_name", "phone"]
    filterset_fields = [
        "student_type",
        "education_lang",
        "marketing_channel",
        "student_stage_type",
        "balance_status",
        "is_archived",
        "sales_manager",
        "call_operator",
    ]

    filterset_class = StudentFilter

    def get_serializer(self, *args, **kwargs):

        # super().get_serializer()

        serializer_class = self.get_serializer_class()
        kwargs.setdefault("context", self.get_serializer_context())
        return serializer_class(
            *args,
            **kwargs,
            include_only=[
                "id",
                "photo",
                "first_name",
                "last_name",
                "middle_name",
                "phone",
                "balance",
                "learning",
                "student_stage_type",
                # "teacher",
                # "secondary_teacher",
                "balance_status",
                "service_manager",
                "sales_manager",
                # "attendance_count",
                "group",
                "created_at",
                "active_date",
                "is_frozen",
                # "secondary_group"
                # new freeze part added,
                "frozen_days",
                "frozen_from_date",
                "frozen_till_date",
            ],
        )

    def get_queryset(self):
        """
        Customize queryset filtering based on user roles and other criteria.
        """

        # queryset = self.queryset.filter(filial=user.filial.first())
        queryset = self.queryset.filter(is_archived=False)

        # Add filters based on query parameters (for sales managment and operators)
        sales_manager_id = self.request.GET.get("sales_manager")
        call_operator_id = self.request.GET.get("call_operator")
        from_price = self.request.GET.get("from_price")
        edu_langauge = self.request.GET.get("language")
        to_price = self.request.GET.get("to_price")
        course_id = self.request.GET.get("course")
        teacher_id = self.request.GET.get("teacher")
        service_manager = self.request.GET.get("service_manager")
        group_id = self.request.GET.get("group")
        subject_id = self.request.GET.get("subject")
        filial_id = self.request.GET.get("filial")
        student_stage_type = self.request.GET.get("stt")

        queryset = queryset.annotate(
            attendance_count=Count(
                "attendances", filter=Q(attendances__status="IS_PRESENT")
            )
        )

        if student_stage_type:
            queryset = queryset.filter(student_stage_type=student_stage_type)

        if filial_id:
            queryset = queryset.filter(filial__id=filial_id)

        if teacher_id:
            queryset = queryset.filter(groups__group__teacher__id=teacher_id)

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
                groups__group__course__id=course_id
            )  # Assuming Many-to-Many relation in groups
        if service_manager:
            queryset = queryset.filter(service_manager__id=service_manager)

        if group_id:
            queryset = queryset.filter(groups__group__id=group_id)

        start_date = self.request.GET.get("start_date")
        end_date = self.request.GET.get("end_date")

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

        return queryset.select_related(
            "photo", "service_manager", "sales_manager"
        ).order_by('check_is_frozen')


class StudentDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [IsAuthenticated]


class StudentListNoPG(FilialRestrictedQuerySetMixin, ListAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        filial_id = self.request.GET.get("filial")
        queryset = Student.objects.all()
        if filial_id:
            queryset = queryset.filter(filial__id=filial_id, is_archived=False)

        return queryset

    def get_paginated_response(self, data):
        return Response(data)


# class StudentScheduleView(FilialRestrictedQuerySetMixin, ListAPIView):
#     serializer_class = LessonSerializer
#     permission_classes = [IsAuthenticated]

#     def get_queryset(self):
#         student_groups = StudentGroup.objects.filter(
#             student_id=self.kwargs["pk"]
#         ).values_list("group_id", flat=True)
#         return Lesson.objects.filter(group_id__in=student_groups).order_by(
#             "day", "start_time"
#         )


class StudentStatistics(FilialRestrictedQuerySetMixin, ListAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        filial = self.request.GET.get("filial")

        filter = {}
        if filial:
            filter["filial__id"] = filial
            ic(filial)
        new_students_count = Student.objects.filter(
            is_archived=False, student_stage_type="NEW_STUDENT", **filter
        ).count()
        total_debt = (
            Student.objects.filter(
                is_archived=False,
                student_stage_type="NEW_STUDENT",
                balance__lt=0,
                **filter,
            ).aggregate(total_debt=Sum("balance"))["total_debt"]
            or 0
        )
        archived_new_students = Student.objects.filter(
            is_archived=True, student_stage_type="NEW_STUDENT", **filter
        ).count()

        # Ordered statistics
        student_count = Student.objects.filter(
            is_archived=False, student_stage_type="ACTIVE_STUDENT", **filter
        ).count()
        total_income = (
            Student.objects.filter(
                is_archived=False,
                student_stage_type="ACTIVE_STUDENT",
                balance__gt=0,
                **filter,
            ).aggregate(total_income=Sum("balance"))["total_income"]
            or 0
        )
        student_total_debt = (
            Student.objects.filter(
                is_archived=False,
                student_stage_type="ACTIVE_STUDENT",
                balance__lt=0,
                **filter,
            ).aggregate(total_debt=Sum("balance"))["total_debt"]
            or 0
        )

        balance_active = Student.objects.filter(
            is_archived=False, balance_status="ACTIVE", **filter
        ).count()

        archived_student = Student.objects.filter(
            is_archived=True, student_stage_type="ACTIVE_STUDENT", **filter
        ).count()

        from_new_to_active = Finance.objects.filter(
            student__isnull=False,
            student__student_stage_type="ACTIVE_STUDENT",
            attendance__isnull=False,
            is_first=True,
            **filter,
        ).count()

        almost_debt = Student.objects.filter(
            is_archived=False, balance__lte=0, balance__gte=100000, **filter
        ).count()

        statistics = {
            "new_students_count": new_students_count,
            "new_to_active": from_new_to_active,
            "new_students_total_debt": total_debt,
            "archived_new_students": archived_new_students,
        }

        # Additional ordered statistics (could be pagination or other stats)
        ordered_statistics = {
            "student_count": student_count,
            "balance_active": balance_active,
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
        filial = self.request.GET.get("filial")
        if filial:
            filter["filial__id"] = filial

        all_students = Student.objects.filter(is_archived=False, **filter).count()
        archived_students = Student.objects.filter(is_archived=True, **filter).count()
        if StudentGroup.student:
            course_ended = StudentGroup.objects.filter(group__status="INACTIVE").count()
        else:
            course_ended = StudentGroup.objects.filter(
                group__status="INACTIVE",
            ).count()
        balance_active = Student.objects.filter(
            is_archived=False,
            **filter,
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
                "student_stage_type",
                openapi.IN_QUERY,
                description="Filter by student stage type",
                type=openapi.TYPE_STRING,
            ),
        ],
        responses={200: "Excel file generated"},
    )
    def get(self, request):
        start_date_str = request.GET.get("start_date")
        end_date_str = request.GET.get("end_date")
        student_stage_type = request.GET.get("student_stage_type")
        sales_manager_id = self.request.GET.get("sales_manager")
        call_operator_id = self.request.GET.get("call_operator")
        from_price = self.request.GET.get("from_price")
        edu_langauge = self.request.GET.get("language")
        to_price = self.request.GET.get("to_price")
        balance_status = self.request.GET.get("balance_status")
        course_id = self.request.GET.get("course")
        teacher_id = self.request.GET.get("teacher")
        service_manager = self.request.GET.get("service_manager")
        group_id = self.request.GET.get("group")
        subject_id = self.request.GET.get("subject")
        filial_id = self.request.GET.get("filial")
        is_archived = self.request.GET.get("is_archived")

        queryset = Student.objects.all()

        if balance_status:
            queryset = queryset.filter(balance_status=balance_status)

        if is_archived:
            queryset = queryset.filter(is_archived=is_archived.capitalize())

        if filial_id:
            queryset = queryset.filter(filial__id=filial_id)

        if teacher_id:
            queryset = queryset.filter(groups__group__teacher__id=teacher_id)

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
            queryset = queryset.filter(groups__group__course__id=course_id)

        if service_manager:
            queryset = queryset.filter(service_manager__id=service_manager)

        if group_id:
            queryset = queryset.filter(groups__group__id=group_id)

        date_format = "%Y-%m-%d"
        if start_date_str and end_date_str:
            start_date = datetime.strptime(start_date_str, date_format).date()
            end_date = datetime.strptime(end_date_str, date_format).date()

            start_datetime = datetime.combine(start_date, datetime.min.time())
            end_datetime = datetime.combine(end_date, datetime.max.time())

            queryset = queryset.filter(created_at__range=(start_datetime, end_datetime))

        elif start_date_str:
            start_date = datetime.strptime(start_date_str, date_format).date()
            start_datetime = datetime.combine(start_date, datetime.min.time())
            end_datetime = datetime.combine(start_date, datetime.max.time())

            queryset = queryset.filter(created_at__range=(start_datetime, end_datetime))
        if filial_id:
            queryset = queryset.filter(filial__id=filial_id)

        if student_stage_type:
            queryset = queryset.filter(student_stage_type=student_stage_type)

        workbook = Workbook()
        sheet = workbook.active
        sheet.title = "Student Data"

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
            "O'quvchi varonkasi",
            "Balansi",
            "Balans statusi",
            "Arxivlangan",
            "Call Operator",
            "Service manager",
            "Yaratilgan vaqti",
        ]
        sheet.append(headers)

        for student in queryset:
            sheet.append(
                [
                    student.first_name,
                    student.last_name,
                    student.phone,
                    (
                        student.date_of_birth.strftime("%d-%m-%Y")
                        if student.date_of_birth
                        else ""
                    ),
                    (
                        "Uzbek tili"
                        if student.education_lang == "UZB"
                        else (
                            "Ingliz tili"
                            if student.education_lang == "ENG"
                            else "Rus tili" if student.education_lang == "RU" else ""
                        )
                    ),
                    (
                        "Maktab"
                        if student.edu_class == "SCHOOL"
                        else (
                            "Universitet"
                            if student.edu_class == "UNIVERSITY"
                            else (
                                "Voyaga yetgan" if student.edu_class == "MATURE" else ""
                            )
                        )
                    ),
                    student.subject.name if student.subject else "",
                    student.ball,
                    student.filial.name if student.filial else "",
                    student.marketing_channel.name if student.marketing_channel else "",
                    (
                        "Yangi student"
                        if student.student_stage_type == "NEW_STUDENT"
                        else "Faol student"
                    ),
                    student.balance if student.balance else 0,
                    (
                        "Haqdor"
                        if student.balance_status == "ACTIVE"
                        else "Qarzdor" if student.balance_status else ""
                    ),
                    "Ha" if student.is_archived else "Yo'q",
                    student.call_operator.full_name if student.call_operator else "",
                    (
                        student.service_manager.full_name
                        if student.service_manager
                        else ""
                    ),
                    (
                        student.created_at.strftime("%d-%m-%Y %H:%M:%S")
                        if student.created_at
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

        response = HttpResponse(
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        response["Content-Disposition"] = 'attachment; filename="Lids_Data.xlsx"'
        workbook.save(response)

        return response


class FistLesson_dataList(ListCreateAPIView):
    queryset = FirstLLesson.objects.all()
    serializer_class = FirstLessonSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = FirstLLesson.objects.all()
        id = self.request.GET.get("id")

        print(id)

        if id:
            queryset = queryset.filter(lid__id=id)
            print(queryset)
        return queryset

    def get_paginated_response(self, data):
        return Response(data)


class FirstLesson_dataListRetrive(RetrieveUpdateDestroyAPIView):
    queryset = FirstLLesson.objects.all()
    serializer_class = FirstLessonSerializer
    permission_classes = [IsAuthenticated]


class CheckPhoneAPIView(APIView):

    def get(self, request: HttpRequest | Request):

        phone_number = request.GET.get("phone_number")

        if phone_number is None:
            return Response(
                {"dfiogujsdpfogijdsfg": "sdfrgl;ijuhsdfg;isdfhjug"}, status=400
            )

        print(phone_number)

        student = Student.objects.filter(phone=phone_number).first()

        if student is None:
            return Response(
                {"exists": False, "user": None, "phone_number": phone_number}
            )

        return Response({"exists": True, "user": StudentSerializer(student).data})


class FirstLessonStatistics(APIView):

    def get(self, request, *args, **kwargs):

        filial = request.GET.get("filial")
        lid_stage_type = request.GET.get("lid_stage_type")
        lid_stages = request.GET.get("lid_stages")
        ordered_stages = request.GET.get("ordered_stages")
        is_archived = request.GET.get("is_archived")
        is_frozen = request.GET.get("is_frozen")
        is_student = request.GET.get("is_student")
        service_manager = request.GET.get("service_manager")
        sales_manager = request.GET.get("sales_manager")
        call_operator = request.GET.get("call_operator")
        ordered_date = request.GET.get("ordered_date")
        subject = request.GET.get("subject")
        edu_class = request.GET.get("edu_class")
        education_lang = request.GET.get("education_lang")

        filters = {
            "filial__id": filial,
            "lid_stage_type": lid_stage_type,
            "lid_stages": lid_stages,
            "ordered_stages": ordered_stages,
            "is_archived": is_archived.capitalize(),
            "is_frozen": is_frozen.capitalize(),
            "is_student": is_student.capitalize(),
            "service_manager__id": service_manager,
            "sales_manager__id": sales_manager,
            "call_operator__id": call_operator,
            "ordered_date": ordered_date,
            "subject__id": subject,
            "edu_class": edu_class,
            "education_lang": education_lang,
        }

        debt = Lid.objects.filter(balance__lt=0, **filters)
        no_debt = Lid.objects.filter(balance__gte=0, **filters)

        debt_amount = (
            Lid.objects.filter(balance__lt=0, **filters).aggregate(
                total=Sum("balance")
            )["total"]
            or 0
        )
        no_debt_amount = (
            Lid.objects.filter(balance__gte=0, **filters).aggregate(
                total=Sum("balance")
            )["total"]
            or 0
        )

        return Response(
            {
                "debt": debt.count(),
                "no_debt": no_debt.count(),
                "debt_amount": debt_amount,
                "no_debt_amount": no_debt_amount,
            }
        )


class StudentArchiveAPIView(APIView):

    def post(self, request: HttpRequest | Request, pk: str):
        student = get_object_or_404(Student, pk=pk)

        if student.is_archived:
            raise ValidationError("Student is already archived")

        # Validate comment
        comment = request.data.get("comment")
        if not comment or not str(comment).strip():
            raise ValidationError({"comment": "This field is required."})

        with transaction.atomic():
            groups = student.groups.filter(is_archived=False)

            for group in groups:
                group.archive("Student archivelandi")

            student.archive(
                comment.strip(),
                archived_by=request.user if request.user.is_authenticated else None,
            )

            # TODO: Write fines for employees

            return Response({"ok": True})
