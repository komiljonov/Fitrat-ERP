import io
from datetime import timedelta, datetime

import icecream
from django.db.models import Q
from django.http import HttpResponse
from django.utils.dateparse import parse_date
from django.utils.timezone import now
from django_filters.rest_framework import DjangoFilterBackend
from openpyxl import Workbook
from openpyxl.utils import get_column_letter
from rest_framework import status
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.generics import ListCreateAPIView, ListAPIView, RetrieveUpdateDestroyAPIView, CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Archived, Frozen
from .serializers import ArchivedSerializer, StuffArchivedSerializer, FrozenSerializer
from ..new_lid.models import Lid
from ...account.models import CustomUser


class ArchivedListAPIView(ListCreateAPIView):
    queryset = Archived.objects.all()
    serializer_class = ArchivedSerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)

    search_fields = ('reason',)
    filterset_fields = ('reason',)
    ordering_fields = ('reason',)

    def get_queryset(self):
        queryset = Archived.objects.all()

        get = self.request.GET.get

        lid = get('lid')
        student = get('student')
        student_stage = get('student_stage')
        lid_stage = get('lid_stage')
        creator = get('creator')
        comment = get('comment')
        is_archived = get('is_archived')
        lang = get('lang')
        subject = get('subject')
        call_operator = get('call_operator')
        sales_manager = get('sales_manager')
        service_manager = get('service_manager')
        balance_from = get('balance_from')
        balance_to = get('balance_to')
        start_date = get('start_date')
        end_date = get('end_date')
        filial = get("filial")
        debts = get("debts")
        no_debts = get("no_debts")

        if no_debts:
            # Student or lid exists and their balance is >= 100000
            queryset = queryset.filter(
                Q(student__isnull=False, student__balance__gte=100000) |
                Q(lid__isnull=False, lid__balance__gte=100000, lid__is_student=False)
            )

        if debts:
            # Student or lid exists and their balance is < 100000
            queryset = queryset.filter(
                Q(student__isnull=False, student__balance__lt=100000) |
                Q(lid__isnull=False, lid__balance__lt=100000, lid__is_student=False)
            )
        if student_stage:
            queryset = queryset.filter(student__student_stage_type=student_stage)
        if lid_stage:
            queryset = queryset.filter(lid__lid_stage_type=lid_stage)
        if filial:
            queryset = queryset.filter(Q(student__filial__id=filial) | Q(lid__filial__id=filial))
        if is_archived:
            queryset = queryset.filter(is_archived=is_archived.capitalize())
        if lid:
            queryset = queryset.filter(lid__id=lid)
        if student:
            queryset = queryset.filter(student__id=student)
        if creator:
            queryset = queryset.filter(creator__id=creator)
        if comment:
            queryset = queryset.filter(comment__icontains=comment)

        if lang:
            queryset = queryset.filter(Q(student__education_lang=lang) | Q(lid__education_lang=lang))
        if subject:
            queryset = queryset.filter(Q(student__subject__id=subject) | Q(lid__subject__id=subject))
        if call_operator:
            queryset = queryset.filter(
                Q(student__call_operator__id=call_operator) | Q(lid__call_operator__id=call_operator))
        if sales_manager:
            queryset = queryset.filter(
                Q(student__sales_manager__id=sales_manager) | Q(lid__sales_manager__id=sales_manager))
        if service_manager:
            queryset = queryset.filter(
                Q(student__service_manager__id=service_manager) | Q(lid__service_manager__id=service_manager))

        if balance_from or balance_to:
            student_q = Q()
            lid_q = Q()

            if balance_from:
                student_q &= Q(student__balance__gte=balance_from)
                lid_q &= Q(lid__balance__gte=balance_from)
            if balance_to:
                student_q &= Q(student__balance__lte=balance_to)
                lid_q &= Q(lid__balance__lte=balance_to)

            queryset = queryset.filter(student_q | lid_q)

        # handle date
        if start_date and end_date:
            try:
                start = parse_date(start_date)
                end = parse_date(end_date)
                if start and end:
                    end_dt = end + timedelta(days=1) - timedelta(seconds=1)
                    queryset = queryset.filter(created__gte=start, created__lte=end_dt)
            except Exception:
                pass
        elif start_date:
            try:
                start = parse_date(start_date)
                if start:
                    queryset = queryset.filter(created__gte=start)
            except Exception:
                pass

        return queryset


class ArchivedDetailAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Archived.objects.all()
    serializer_class = ArchivedSerializer
    permission_classes = (IsAuthenticated,)


class ListArchivedListNOPgAPIView(ListAPIView):
    queryset = Archived.objects.all()
    serializer_class = ArchivedSerializer
    permission_classes = (IsAuthenticated,)

    def get_paginated_response(self, data):
        return Response(data)


class StudentArchivedListAPIView(ListAPIView):
    queryset = Archived.objects.all()
    serializer_class = ArchivedSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        queryset = Archived.objects.all()

        id = self.request.query_params.get('id', None)
        print(id)
        if id:
            queryset = queryset.filter(Q(student__id=id) | Q(lid__id=id))
        return queryset


class StuffArchive(CreateAPIView):
    serializer_class = StuffArchivedSerializer
    permission_classes = (IsAuthenticated,)

    def create(self, request, *args, **kwargs):
        user = CustomUser.objects.filter(id=request.data.get('stuff')).first()  # Birinchi foydalanuvchini olish

        icecream.ic(user)  # Debug uchun

        if user:
            if not user.is_archived:
                user.is_archived = True
                user.save()
                return Response({"message": "Xodim arxivlandi!"}, status=status.HTTP_200_OK)
            return Response({"error": "Xodim arxivlangan, qayta arxivlash amalga oshirib bulmaydi!"},
                            status=status.HTTP_400_BAD_REQUEST)

        return Response({"error": "Xodim topilmadi!"}, status=status.HTTP_404_NOT_FOUND)


class FrozenListCreateList(ListCreateAPIView):
    queryset = Frozen.objects.all()
    serializer_class = FrozenSerializer

    def get_queryset(self):
        queryset = Frozen.objects.all()

        creator = self.request.GET.get('creator')
        lid = self.request.GET.get('lid')
        student = self.request.GET.get('student')

        if creator:
            queryset = queryset.filter(creator__id=creator)
        if lid:
            queryset = queryset.filter(lid__id=lid)
        if student:
            queryset = queryset.filter(student__id=student)
        return queryset


class FrozenDetailAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Frozen.objects.all()
    serializer_class = FrozenSerializer
    permission_classes = (IsAuthenticated,)


class ExportLidsExcelView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        queryset = Lid.objects.all()
        filters = {}

        # Query params
        filial = request.GET.get("filial")
        is_archived = request.GET.get("is_archived")
        call_operator = request.GET.get("call_operator")
        service_manager = request.GET.get("service_manager")
        sales_manager = request.GET.get("sales_manager")
        is_student = request.GET.get("is_student")
        start_date_str = request.GET.get("start_date")
        end_date_str = request.GET.get("end_date")

        if filial:
            filters["filial__id"] = filial
        if is_archived is not None:
            filters["is_archived"] = is_archived.lower() == "true"
        if call_operator:
            filters["call_operator__id"] = call_operator
        if service_manager:
            filters["service_manager__id"] = service_manager
        if sales_manager:
            filters["sales_manager__id"] = sales_manager
        if is_student is not None:
            filters["is_student"] = is_student.lower() == "true"

        # Date range
        date_format = "%Y-%m-%d"
        if start_date_str and end_date_str:
            start_date = datetime.strptime(start_date_str, date_format)
            end_date = datetime.strptime(end_date_str, date_format) + timedelta(days=1)
            filters["created_at__gte"] = start_date
            filters["created_at__lt"] = end_date
        elif start_date_str:
            start_date = datetime.strptime(start_date_str, date_format)
            end_date = start_date + timedelta(days=1)
            filters["created_at__gte"] = start_date
            filters["created_at__lt"] = end_date

        # Access limitation
        if user.role == "CALL_OPERATOR" or getattr(user, "is_call_center", False):
            queryset = queryset.filter(
                Q(filial__in=user.filial.all()) | Q(filial__isnull=True),
                Q(call_operator=user) | Q(call_operator__isnull=True)
            )
        else:
            queryset = queryset.filter(Q(filial__in=user.filial.all()) | Q(filial__isnull=True))

        lids = queryset.filter(**filters)

        # Generate Excel
        wb = Workbook()
        ws = wb.active
        ws.title = "Lidlar ro'yxati"

        headers = [
            "Ism", "Familiya", "Sharif", "Telefon", "Qo‘shimcha raqam",
            "Tug‘ilgan sana", "Ta’lim tili", "O‘quv darajasi",
            "Fan", "Ball", "Filial", "Marketing kanali", "Lid bosqichi turi",
            "Lid bosqichi", "Buyurtma bosqichi", "Arxivlanganmi?",
            "Muzlatilganmi?", "Call operator", "Servis menejeri", "Sotuv menejeri",
            "Studentmi?", "Balans"
        ]
        ws.append(headers)

        for lid in lids:
            row = [
                lid.first_name,
                lid.last_name or "",
                lid.middle_name or "",
                lid.phone_number or "",
                lid.extra_number or "",
                lid.date_of_birth.strftime("%Y-%m-%d") if lid.date_of_birth else "",
                lid.education_lang,
                lid.edu_level or "",
                lid.subject.name if lid.subject else "",
                lid.ball or 0,
                lid.filial.name if lid.filial else "",
                lid.marketing_channel.name if lid.marketing_channel else "",
                lid.lid_stage_type,
                lid.lid_stages or "",
                lid.ordered_stages or "",
                "Ha" if lid.is_archived else "Yo‘q",
                "Ha" if lid.is_frozen else "Yo‘q",
                lid.call_operator.get_full_name() if lid.call_operator else "",
                lid.service_manager.get_full_name() if lid.service_manager else "",
                lid.sales_manager.get_full_name() if lid.sales_manager else "",
                "Ha" if lid.is_student else "Yo‘q",
                float(lid.balance or 0),
            ]
            ws.append(row)

        for col in ws.columns:
            max_length = max(len(str(cell.value)) if cell.value else 0 for cell in col)
            ws.column_dimensions[get_column_letter(col[0].column)].width = max_length + 4

        buffer = io.BytesIO()
        wb.save(buffer)
        buffer.seek(0)

        response = HttpResponse(
            buffer.read(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        filename = f"lidlar_{now().strftime('%Y%m%d_%H%M')}.xlsx"
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        return response


class LidStudentArchivedStatistics(APIView):
    def get(self, request, *args, **kwargs):
        queryset = Archived.objects.filter(is_archived=True)

        # --- Filters ---
        is_lid = request.GET.get("is_lid", "") == "true"
        education_lang = request.GET.get("education_lang")
        subject = request.GET.get("subject")
        call_operator = request.GET.get("call_operator")
        service_manager = request.GET.get("service_manager")
        sales_manager = request.GET.get("sales_manager")
        balance_from = request.GET.get("balance_from")
        balance_to = request.GET.get("balance_to")
        start_date = parse_date(request.GET.get("start_date", ""))
        end_date = parse_date(request.GET.get("end_date", ""))

        if is_lid:
            queryset = queryset.filter(lid__isnull=False)
        elif is_lid == False:
            queryset = queryset.filter(student__isnull=False)

        if education_lang:
            field = "lid__education_lang" if is_lid else "student__education_lang"
            queryset = queryset.filter(**{field: education_lang})

        if subject:
            field = "lid__subject__id" if is_lid else "student__subject__id"
            queryset = queryset.filter(**{field: subject})

        if call_operator:
            field = "lid__call_operator__id" if is_lid else "student__call_operator__id"
            queryset = queryset.filter(**{field: call_operator})

        if service_manager:
            field = "lid__service_manager__id" if is_lid else "student__service_manager__id"
            queryset = queryset.filter(**{field: service_manager})

        if sales_manager:
            field = "lid__sales_manager__id" if is_lid else "student__sales_manager__id"
            queryset = queryset.filter(**{field: sales_manager})

        if balance_from and balance_to:
            field_from = "lid__balance_from__lte" if is_lid else "student__balance_from__lte"
            field_to = "lid__balance_to__gte" if is_lid else "student__balance_to__gte"
            queryset = queryset.filter(**{
                field_from: balance_from,
                field_to: balance_to
            })
        elif balance_from:
            field = "lid__balance_from__lte" if is_lid else "student__balance_from__lte"
            queryset = queryset.filter(**{field: balance_from})

        if start_date and end_date:
            queryset = queryset.filter(
                created_at__gte=start_date,
                created_at__lte=end_date + timedelta(days=1) - timedelta(seconds=1)
            )
        elif start_date:
            queryset = queryset.filter(
                created_at__gte=start_date,
                created_at__lte=start_date + timedelta(days=1) - timedelta(seconds=1)
            )

        # --- Stats ---
        all_archived = queryset.count()
        archived_lids = queryset.filter(lid__isnull=False, lid__lid_stage_type="NEW_LID").count()
        archived_orders = queryset.filter(lid__isnull=False,
                                          lid__lid_stage_type="ORDERED_LID").count()  # or another field for "order"
        archived_new_students = queryset.filter(student__isnull=False,
                                                student__student_stage_type="NEW_STUDENT").count()
        archived_active_students = queryset.filter(student__isnull=False,
                                                   student__student_stage_type="ACTIVE_STUDENT").count()
        debt_lid = queryset.filter(lid__isnull=False, lid__balance__gte=100000).count()
        deb_student = queryset.filter(student__isnull=False, student__balance__gte=100000).count()

        no_debt_lid = queryset.filter(lid__isnull=False, lid__balance__lte=100000).count()
        no_debt_student = queryset.filter(student__isnull=False, student__balance__lte=100000).count()

        return Response({
            "debt": debt_lid + deb_student,
            "no_debt": no_debt_lid + no_debt_student,

            "all_archived": all_archived,
            "archived_lids": archived_lids,
            "archived_orders": archived_orders,
            "archived_new_students": archived_new_students,
            "archived_active_students": archived_active_students,

        })
