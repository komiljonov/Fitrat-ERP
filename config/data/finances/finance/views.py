import datetime
from datetime import datetime, timedelta

import openpyxl
import pandas as pd
from django.db.models import Q
from django.db.models import Sum
from django.http import HttpResponse
from django.utils import timezone
from django.utils.dateparse import parse_datetime, parse_date
from django.utils.timezone import make_aware
from django.utils.timezone import now
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from icecream import ic
from rest_framework import status
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.generics import ListAPIView, ListCreateAPIView, RetrieveUpdateDestroyAPIView, CreateAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from data.account.models import CustomUser
from data.finances.finance.models import Finance, Kind  # adjust if needed
from data.student.student.models import Student
from .models import Casher, Handover, PaymentMethod, Sale, SaleStudent, Voucher, VoucherStudent
from .serializers import FinanceSerializer, CasherSerializer, CasherHandoverSerializer, KindSerializer, \
    PaymentMethodSerializer, SalesSerializer, SaleStudentSerializer, VoucherSerializer, VoucherStudentSerializer
from ...lid.new_lid.models import Lid
from ...student.attendance.models import Attendance
from ...student.groups.models import Group


class CasherListCreateAPIView(ListCreateAPIView):
    queryset = Casher.objects.all()
    serializer_class = CasherSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        role = self.request.query_params.get('role', None)
        is_archived = self.request.GET.get('is_archived', False)

        filter = {}

        if is_archived:
            filter['is_archived'] = is_archived.capitalize()
        if role:
            filter['role'] = role

        return Casher.objects.filter(filial=self.request.user.filial.first(), **filter)


class CasherRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Casher.objects.all()
    serializer_class = CasherSerializer
    permission_classes = [IsAuthenticated]


class CasherNoPg(ListAPIView):
    queryset = Casher.objects.all()
    serializer_class = CasherSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        role = self.request.query_params.get('role', None)

        filter = {}
        if role:
            filter['role'] = role

        return Casher.objects.filter(filial=self.request.user.filial.first(), **filter)

    def get_paginated_response(self, data):
        return Response(data)


class FinanceListAPIView(ListCreateAPIView):
    queryset = Finance.objects.all()
    serializer_class = FinanceSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        kind = self.request.query_params.get('kind')
        action = self.request.query_params.get('action')
        start_date_str = self.request.query_params.get('start_date')
        end_date_str = self.request.query_params.get('end_date')
        casher_id = self.request.query_params.get('casher_id')

        queryset = Finance.objects.all().exclude(Q(kind__name__icontains="Bonus") | Q(kind__name__icontains="Money back"))

        if action:
            queryset = queryset.filter(action=action)

        if casher_id:
            queryset = queryset.filter(casher__id=casher_id)

        if kind:
            try:
                kind_obj = Kind.objects.get(id=kind)
                queryset = queryset.filter(kind=kind_obj)
            except Kind.DoesNotExist:
                return Finance.objects.none()

        if start_date_str:
            start = parse_date(start_date_str)
            if not start:
                return Finance.objects.none()

            if end_date_str:
                end = parse_date(end_date_str)
                if not end:
                    end = start
            else:
                end = start

            # Add one day to end for exclusive filtering
            end_dt = datetime.combine(end, datetime.min.time()) + timedelta(days=1)
            end_dt = make_aware(end_dt)

            queryset = queryset.filter(
                created_at__gte=datetime.combine(start, datetime.min.time()),
                created_at__lt=end_dt
            )

        return queryset


class FinanceDetailAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Finance.objects.all()
    serializer_class = FinanceSerializer
    permission_classes = (IsAuthenticated,)


class FinanceNoPGList(ListAPIView):
    queryset = Finance.objects.all()
    serializer_class = FinanceSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = None

    def get_paginated_response(self, data):
        return Response(data)


class StudentFinanceListAPIView(ListAPIView):
    serializer_class = FinanceSerializer
    permission_classes = (IsAuthenticated,)

    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    search_fields = ("action", "kind")
    ordering_fields = ("action", "kind")
    filterset_fields = ("action", "kind")

    def get_queryset(self, **kwargs):
        # Initialize the queryset to all Finance records
        queryset = Finance.objects.all()

        # Get the pk from the URL kwargs
        pk = self.kwargs.get('pk')

        # Try to fetch the student or lid based on the pk
        student = Student.objects.filter(id=pk).first()  # Safer query, returns None if not found
        lid = Lid.objects.filter(id=pk).first()  # Safer query for lid, returns None if not found

        # Filter by student or lid if present
        if student:
            queryset = queryset.filter(student=student)
        elif lid:
            queryset = queryset.filter(lid=lid)

        start_date = self.request.query_params.get("start_date")
        end_date = self.request.query_params.get("end_date")

        if start_date and end_date:
            try:
                # Parse and filter by date range
                start_date = parse_datetime(start_date).date()
                end_date = parse_datetime(end_date).date()
                queryset = queryset.filter(created_at__range=[start_date, end_date])
            except ValueError:
                pass  # Handle invalid date format, if necessary
        elif start_date:
            try:
                # Parse and filter by start date
                start_date = parse_datetime(start_date).date()
                queryset = queryset.filter(created_at__date=start_date)
            except ValueError:
                pass  # Handle invalid date format, if necessary
        elif end_date:
            try:
                # Parse and filter by end date
                end_date = parse_datetime(end_date).date()
                queryset = queryset.filter(created_at__date=end_date)
            except ValueError:
                pass  # Handle invalid date format, if necessary

        # Return queryset (even if it's empty, which will result in no matching records)
        return queryset


class StuffFinanceListAPIView(ListAPIView):
    queryset = Finance.objects.all()
    serializer_class = FinanceSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self, **kwargs):
        stuff = CustomUser.objects.get(id=self.kwargs.get('pk'))

        if stuff:
            return Finance.objects.filter(stuff=stuff)
        return Finance.objects.none()


class FinancePaymentMethodsAmountsListAPIView(APIView):

    def get(self, request):
        payment_method = request.GET.get('payment_method')
        filial = request.GET.get('filial')
        casher_id = request.GET.get('casher')

        casher_obj = Casher.objects.filter(id=casher_id).first()

        income = Finance.objects.filter(
            casher=casher_obj,
            action='INCOME',
            payment_method=payment_method
        ).aggregate(Sum('amount'))['amount__sum'] or 0

        expense = Finance.objects.filter(
            casher=casher_obj,
            action='EXPENSE',
            payment_method=payment_method
        ).aggregate(Sum('amount'))['amount__sum'] or 0

        return Response({
            'income_amount': income,
            'expense_amount': expense,
            "payment_method": payment_method,
            "filial": filial,
            "casher": casher_obj.name,
            "current_amount": income - expense,
        })


class CasherHandoverAPIView(CreateAPIView):
    serializer_class = CasherHandoverSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        receiver = serializer.validated_data.get("receiver")
        casher = serializer.validated_data.get("casher")
        amount = serializer.validated_data.get("amount")
        payment_method = serializer.validated_data.get("payment_method")

        if int(amount) > 0:
            # Get the Kind instance (unpacking the tuple)
            handover, _ = Kind.objects.get_or_create(name="CASHIER_HANDOVER", action="EXPENSE")

            # Deduct from sender (casher)
            Finance.objects.create(
                casher=casher,
                amount=amount,
                payment_method=payment_method,
                action='EXPENSE',
                kind=handover,
                creator=request.user,
                comment=f"{casher.name}  - {amount}  so'm  "
                        f"{receiver.name}  ga kassa topshirdi ."
            )

            # Get the Kind instance (unpacking the tuple)
            acception, _ = Kind.objects.get_or_create(name="CASHIER_ACCEPTANCE", action="INCOME")

            # Add to receiver
            Finance.objects.create(
                casher=receiver,
                amount=amount,
                payment_method=payment_method,
                action='INCOME',
                kind=acception,
                creator=request.user,
                comment=f"{receiver.name}  - {amount}  so'm  "
                        f"{casher.name}  dan kassa qabul qildi ."
            )

            Handover.objects.create(
                amount=amount,
                receiver=receiver,
                casher=casher,
            )

            return Response(
                {"message": "Cashier handover completed successfully"},
                status=status.HTTP_201_CREATED
            )

        return Response(
            {"error": "Insufficient balance for handover"},
            status=status.HTTP_400_BAD_REQUEST
        )


class FinanceStatisticsAPIView(APIView):
    # permission_classes = [IsAuthenticated]

    def get(self, request):
        kind = self.request.query_params.get("kind", None)
        filial = self.request.query_params.get("filial", None)

        filters = {}
        if kind:
            filters["kind_id"] = kind
        if filial:
            filters["filial_id"] = filial

        def get_balance(role):

            total_income = (
                    Finance.objects.filter(casher__role=role, action="INCOME", **filters)
                    .aggregate(total_income=Sum("amount"))["total_income"] or 0
            )

            total_outcome = (
                    Finance.objects.filter(casher__role=role, action="EXPENSE", **filters)
                    .aggregate(total_outcome=Sum("amount"))["total_outcome"] or 0
            )

            balance = total_income - total_outcome

            ic(role, total_income, total_outcome, balance)
            return balance

        response_data = {
            "main_casher": get_balance("WEALTH"),
            "admin_casher": get_balance("ADMINISTRATOR"),
            "accounting_casher": get_balance("ACCOUNTANT"),
        }

        return Response(response_data)


class CasherHandoverHistory(ListAPIView):
    serializer_class = CasherHandoverSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self, **kwargs):
        casher = self.kwargs.get('pk')
        if casher:
            return Handover.objects.filter(casher__id=casher)
        return Finance.objects.none()


class CasherStatisticsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        casher_id = self.kwargs.get('pk')
        kind_id = request.query_params.get('kind')
        start_date_str = request.query_params.get('start_date')
        end_date_str = request.query_params.get('end_date')

        filters = {}

        # Handle start date
        if start_date_str:
            try:
                start_dt = make_aware(datetime.strptime(start_date_str, "%Y-%m-%d"))
                filters["created_at__gte"] = start_dt

                if not end_date_str:
                    # Set end of day as end date
                    end_dt = start_dt + timedelta(days=1) - timedelta(seconds=1)
                    filters["created_at__lte"] = end_dt
            except ValueError:
                return Response({"error": "Invalid start_date format. Use YYYY-MM-DD."}, status=400)

        # Handle end date
        if end_date_str:
            try:
                end_dt = datetime.strptime(end_date_str, "%Y-%m-%d") + timedelta(days=1) - timedelta(seconds=1)
                end_dt = make_aware(end_dt)
                filters["created_at__lte"] = end_dt
            except ValueError:
                return Response({"error": "Invalid end_date format. Use YYYY-MM-DD."}, status=400)

        # Handle kind filtering
        if kind_id:
            try:
                filters['kind'] = Kind.objects.get(id=kind_id)
            except Kind.DoesNotExist:
                return Response({"error": "Kind not found."}, status=404)

        # Check casher and return results
        if casher_id:
            income = Finance.objects.filter(casher__id=casher_id, action='INCOME', **filters) \
                         .aggregate(Sum('amount'))['amount__sum'] or 0
            expense = Finance.objects.filter(casher__id=casher_id, action='EXPENSE', **filters) \
                          .aggregate(Sum('amount'))['amount__sum'] or 0
            balance = income - expense

            return Response({
                "income": income,
                "expense": expense,
                "balance": balance
            })

        return Response({"error": "Casher ID is required."}, status=400)


class CustomPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class TeacherGroupFinanceAPIView(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination

    def get(self, request, *args, **kwargs):
        teacher_id = self.kwargs.get('pk')
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')

        print("teacher", teacher_id)

        group_filters = {"group__teacher_id": teacher_id}
        if start_date and end_date:
            group_filters["created_at__range"] = (start_date, end_date)
        elif start_date:
            group_filters["created_at__gte"] = start_date

        attended_groups = Attendance.objects.filter(**group_filters).values_list('group_id', flat=True).distinct()

        # Convert to set to ensure uniqueness, then back to list
        unique_group_ids = list(set(attended_groups))

        group_data_list = []
        processed_groups = set()  # Track processed groups to avoid duplicates

        for group_id in unique_group_ids:
            # Skip if already processed
            if group_id in processed_groups:
                continue

            processed_groups.add(group_id)

            # Prepare finance filter
            finance_filters = {"attendance__group__id": group_id}
            if start_date and end_date:
                finance_filters["created_at__range"] = (start_date, end_date)
            elif start_date:
                finance_filters["created_at__gte"] = start_date

            kind = Kind.objects.filter(action="INCOME", name__icontains="Lesson payment").first()
            finance_records = Finance.objects.filter(**finance_filters, stuff__id=teacher_id, kind=kind).order_by(
                "created_at")
            created_at = finance_records.first().created_at if finance_records.exists() else None
            total_group_payment = finance_records.aggregate(Sum('amount'))['amount__sum'] or 0

            # Collect students in group with date filters applied
            student_filters = {"attendance_student__group__id": group_id}
            if start_date and end_date:
                student_filters["attendance_student__created_at__range"] = (start_date, end_date)
            elif start_date:
                student_filters["attendance_student__created_at__gte"] = start_date

            students = Student.objects.filter(**student_filters).distinct()
            student_data = []

            for student in students:
                # Apply date filters to student attendances
                student_attendance_filters = {"group_id": group_id, "student": student}
                if start_date and end_date:
                    student_attendance_filters["created_at__range"] = (start_date, end_date)
                elif start_date:
                    student_attendance_filters["created_at__gte"] = start_date

                student_attendances = Attendance.objects.filter(**student_attendance_filters)
                student_finance_filters = {"attendance__in": student_attendances}

                if start_date and end_date:
                    student_finance_filters["created_at__range"] = (start_date, end_date)
                elif start_date:
                    student_finance_filters["created_at__gte"] = start_date

                if student_attendances.exists():
                    first_attendance = student_attendances.first()
                    # Remove this line as it's too restrictive
                    # student_finance_filters["created_at__date"] = first_attendance.created_at.date()
                    total_student_payment = \
                        Finance.objects.filter(**student_finance_filters, stuff__id=teacher_id, kind=kind).aggregate(
                            Sum('amount'))[
                            'amount__sum'] or 0
                else:
                    total_student_payment = 0

                student_data.append({
                    "student_id": str(student.id),
                    "student_name": f"{student.first_name} {student.last_name}",
                    "total_payment": total_student_payment
                })

            # Get group name more efficiently
            try:
                group = Group.objects.get(id=group_id)
                group_name = group.name
            except Group.DoesNotExist:
                group_name = "Unknown Group"

            group_data_list.append({
                "group_id": str(group_id),
                "group_name": group_name,
                "total_group_payment": total_group_payment,
                "students": student_data,
                "created_at": created_at,
            })

        group_data_list.sort(key=lambda x: x['created_at'] or timezone.now(), reverse=True)

        # Paginate the group data
        paginator = self.pagination_class()
        paginated_data = paginator.paginate_queryset(group_data_list, request)
        return paginator.get_paginated_response(paginated_data)


class FinanceTeacher(ListAPIView):
    serializer_class = FinanceSerializer
    permission_classes = [IsAuthenticated]
    queryset = Finance.objects.all()

    def get_queryset(self):
        teacher = self.request.user
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        ic(teacher)
        if teacher:
            queryset = Finance.objects.filter(
                stuff=teacher,
                attendance__isnull=True
            )
            if start_date:
                queryset = queryset.filter(created_at__gte=start_date)
            if start_date and end_date:
                queryset = queryset.filter(created_at__gte=start_date, created_at__lte=end_date)
            return queryset

        return Finance.objects.none()


class FinanceExcel(APIView):

    def get(self, request, *args, **kwargs):
        filial = request.GET.get('filial')
        casher_id = request.GET.get('cashier')
        casher_role = request.GET.get('casher_role')
        kind_id = request.GET.get('kind')
        action = request.GET.get('action')

        filters = Q()
        if filial:
            filters &= Q(casher__user__filial__id=filial)
        if casher_id:
            filters &= Q(casher__id=casher_id)
        if casher_role:
            filters &= Q(casher__role=casher_role)
        if kind_id:
            filters &= Q(kind__id=kind_id)
        if action:
            filters &= Q(action=action)

        finances = Finance.objects.filter(filters)

        # Create an Excel workbook
        workbook = openpyxl.Workbook()
        sheet = workbook.active
        sheet.title = "Finance Report"

        # Add headers
        headers = ["Cassa egasi", "Role", "To'lov turi", "Action", "Miqdor", "To'lov metodi", "Comment",
                   "Yaratilgan vaqti"]
        sheet.append(headers)

        # Add data
        for finance in finances:
            sheet.append([
                finance.casher.name if finance.casher else "-",
                "Asosiy kassa " if finance.casher.role == "WEALTH" else
                "Buxgalteriya kassa" if finance.casher.role == "ACCOUNTANT" else
                "Filial kassa" if finance.casher.role == "ADMINISTRATOR" else "",
                "Kassa qabul qilish" if finance.kind.name == "CASHIER_ACCEPTANCE" else
                "Kassa topshirish" if finance.kind.name == "CASHIER_HANDOVER" else
                "Oylik maosh" if finance.kind.name == "Salary" else
                "Kurs to'lovi" if finance.kind.name == "Course payment" else
                "1 dars uchun to'lov" if finance.kind.name == "Lesson payment" else
                "Pul qaytarish" if finance.kind.name == "Money back" else
                finance.kind.name if hasattr(finance.kind, "name") else str(finance.kind),  # ✅ Fix applied here
                "Kirim" if finance.action == "INCOME" else "Xarajat",
                finance.amount,
                "Naqt pul" if finance.payment_method == "Cash" else
                "Pul kuchirish" if finance.payment_method == "Money_send" else
                "Karta orqali" if finance.payment_method == "Card" else
                "Payme" if finance.payment_method == "Payme" else "Click",
                finance.comment or "-",
                finance.created_at.strftime("%d-%m-%Y %H:%M:%S"),
            ])

        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="finance_report.xlsx"'
        workbook.save(response)
        return response


class KindList(ListCreateAPIView):
    serializer_class = KindSerializer
    permission_classes = [IsAuthenticated]
    queryset = Kind.objects.all()

    def get_queryset(self):
        kind = self.request.query_params.get('action')
        if kind:
            queryset = Kind.objects.filter(
                action=kind,
            )
            return queryset
        return Kind.objects.none()

    def get_paginated_response(self, data):
        return Response(data)


class KindRetrieve(RetrieveUpdateDestroyAPIView):
    serializer_class = KindSerializer
    permission_classes = [IsAuthenticated]
    queryset = Kind.objects.all()


class PaymentMethodsList(ListCreateAPIView):
    queryset = PaymentMethod.objects.all()
    serializer_class = PaymentMethodSerializer
    permission_classes = [IsAuthenticated]


class PaymentMethodsRetrieve(RetrieveUpdateDestroyAPIView):
    serializer_class = PaymentMethodSerializer
    permission_classes = [IsAuthenticated]
    queryset = PaymentMethod.objects.all()


class PaymentStatistics(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        filial = self.request.query_params.get('filial')
        casher_id = self.request.query_params.get('casher')
        filter = {}

        if casher_id:
            filter['casher__id'] = casher_id
        if filial:
            filter['filial'] = filial
        if start_date:
            filter['created_at__gte'] = start_date
        if end_date:
            filter['created_at__lte'] = end_date

        valid_payment_methods = [
            'Click', 'Payme', 'Cash', 'Card', "Money_send"
        ]

        def get_total_amount(payment_name, action_type):
            return Finance.objects.filter(payment_method=payment_name, action=action_type, **filter).aggregate(
                total=Sum('amount'))['total'] or 0

        data = {}

        for payment in valid_payment_methods:
            formatted_name = payment.lower().replace(" ", "_")
            data[f"{formatted_name}_income"] = get_total_amount(payment, "INCOME")
            data[f"{formatted_name}_expense"] = get_total_amount(payment, "EXPENSE")

        # Compute total income and expense
        data["total_income"] = sum(data[f"{p.lower().replace(' ', '_')}_income"] for p in valid_payment_methods)
        data["total_expense"] = sum(data[f"{p.lower().replace(' ', '_')}_expense"] for p in valid_payment_methods)

        return Response(data)


class PaymentCasherStatistics(ListAPIView):
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        cashier_id = self.kwargs.get('pk')
        start_date_str = request.query_params.get('start_date')
        end_date_str = request.query_params.get('end_date')

        # ✅ Safely parse dates from string to datetime
        start_date = None
        end_date = None
        try:
            if start_date_str:
                start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
            if end_date_str:
                end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
        except ValueError:
            return Response({"error": "Invalid date format. Use YYYY-MM-DD."}, status=400)

        # ✅ Supported payment methods
        valid_payment_methods = ['Click', 'Payme', 'Cash', 'Card', "Money_send"]

        def get_total_amount(payment_method, action_type):
            qs = Finance.objects.filter(payment_method=payment_method, action=action_type)
            if cashier_id:
                qs = qs.filter(casher__id=cashier_id)

            if start_date and not end_date:
                qs = qs.filter(
                    created_at__gte=start_date,
                    created_at__lt=start_date + timedelta(days=1)
                )
            elif start_date and end_date:
                qs = qs.filter(
                    created_at__gte=start_date,
                    created_at__lt=end_date + timedelta(days=1)
                )

            return qs.aggregate(total=Sum('amount'))['total'] or 0

        # ✅ Build statistics data
        data = {}
        for payment in valid_payment_methods:
            key = payment.lower().replace(" ", "_")
            data[f"{key}_income"] = get_total_amount(payment, "INCOME")
            data[f"{key}_expense"] = get_total_amount(payment, "EXPENSE")

        data["total_income"] = sum(data[f"{p.lower().replace(' ', '_')}_income"] for p in valid_payment_methods)
        data["total_expense"] = sum(data[f"{p.lower().replace(' ', '_')}_expense"] for p in valid_payment_methods)

        return Response(data)

    def get_queryset(self):
        return Finance.objects.none()


class SalesList(ListCreateAPIView):
    serializer_class = SalesSerializer
    queryset = Sale.objects.all()
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        filial = self.request.query_params.get('filial')
        if filial:
            return Sale.objects.filter(filial__in=filial)
        return Sale.objects.filter(filial__in=self.request.user.filial.all())


class SalesStudentNoPG(ListAPIView):
    serializer_class = SalesSerializer
    queryset = Sale.objects.all()
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        filial = self.request.query_params.get('filial')
        if filial:
            return Sale.objects.filter(filial__in=filial)
        return Sale.objects.filter(filial__in=self.request.user.filial.all())

    def get_paginated_response(self, data):
        return Response(data)


class SalesStudentList(ListCreateAPIView):
    serializer_class = SaleStudentSerializer
    queryset = SaleStudent.objects.filter(sale__status="ACTIVE")
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        filial = self.request.query_params.get('filial')
        type = self.request.query_params.get('type')

        queryset = SaleStudent.objects.filter(sale__status="ACTIVE")

        if filial:
            queryset = queryset.filter(filial__id=filial)
        if type:
            queryset = queryset.filter(sale__type=type)

        return queryset


class SaleStudentRetrieve(ListAPIView):
    serializer_class = SaleStudentSerializer
    queryset = SaleStudent.objects.all()
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        id = self.kwargs.get('pk')
        if id:
            return SaleStudent.objects.filter(Q(lid__id=id) | Q(student__id=id)).filter(sale__status="ACTIVE")
        return SaleStudent.objects.none()

    def get_paginated_response(self, data):
        return Response(data)


class SalesStudentsRetrieve(RetrieveUpdateDestroyAPIView):
    serializer_class = SaleStudentSerializer
    queryset = SaleStudent.objects.all()
    permission_classes = [IsAuthenticated]


class PaymentStatisticsByKind(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Parse and validate dates
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        filial = request.query_params.get('filial')

        filters = {}
        if start_date:
            start_date = parse_date(start_date)
            filters['created_at__gte'] = start_date
        if end_date:
            end_date = parse_date(end_date)
            filters['created_at__lte'] = end_date
        if filial:
            filters['filial_id'] = filial

        kinds = Kind.objects.all()

        # Function to get total amount for a given kind and action type
        def get_total_amount(kind, action_type):
            return (
                    Finance.objects.filter(kind=kind, action=action_type, **filters)
                    .aggregate(total=Sum('amount'))['total'] or 0
            )

        # Function to get distinct actions for a given kind
        def get_kind_actions(kind):
            return list(
                Finance.objects.filter(kind=kind, **filters)
                .values_list("action", flat=True)
                .distinct()
            )

        data = {}

        for kind in kinds:
            kind_name = kind.name.lower().replace(" ", "_")
            data[kind_name] = {
                "income": get_total_amount(kind, "INCOME"),
                "expense": get_total_amount(kind, "EXPENSE"),
                "action": kind.action,
                "color": kind.color
            }

        # Compute total income and expense **only from kinds**, excluding any integers in data
        total_income = sum(item["income"] for item in data.values() if isinstance(item, dict))
        total_expense = sum(item["expense"] for item in data.values() if isinstance(item, dict))

        data["total_income"] = total_income
        data["total_expense"] = total_expense

        return Response(data)


class VoucherList(ListCreateAPIView):
    serializer_class = VoucherSerializer
    queryset = Voucher.objects.all()
    permission_classes = [IsAuthenticated]


class VoucherRetrieve(RetrieveUpdateDestroyAPIView):
    serializer_class = VoucherSerializer
    queryset = Voucher.objects.all()
    permission_classes = [IsAuthenticated]


class VoucherNoPG(ListAPIView):
    serializer_class = VoucherSerializer
    queryset = Voucher.objects.all()
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        is_expired = self.request.query_params.get('is_expired')
        filial = self.request.query_params.get('filial')

        queryset = Voucher.objects.all()
        if filial:
            queryset = queryset.filter(filial_id=filial)

        if is_expired:
            queryset = queryset.filter(is_expired=is_expired.capitalize())
        return queryset

    def get_paginated_response(self, data):
        return Response(data)


class VoucherStudentList(ListCreateAPIView):
    serializer_class = VoucherStudentSerializer
    queryset = VoucherStudent.objects.all()
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        id = self.request.query_params.get('id')
        if id:
            return VoucherStudent.objects.filter(Q(lid__id=id) | Q(student__id=id))
        else:
            return VoucherStudent.objects.all()


class VoucherStudentRetrieve(RetrieveUpdateDestroyAPIView):
    serializer_class = VoucherStudentSerializer
    queryset = VoucherStudent.objects.all()
    permission_classes = [IsAuthenticated]


class GeneratePaymentExcelAPIView(APIView):
    # permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('casher_id', openapi.IN_QUERY, description="Casher ID (Required)",
                              type=openapi.FORMAT_UUID, required=True),
            openapi.Parameter('start_date', openapi.IN_QUERY, description="Start date (Optional, format: YYYY-MM-DD)",
                              type=openapi.TYPE_STRING),
            openapi.Parameter('end_date', openapi.IN_QUERY, description="End date (Optional, format: YYYY-MM-DD)",
                              type=openapi.TYPE_STRING),
        ],
        responses={
            200: "Excel file containing payment statistics",
            400: "Bad Request - Missing required parameters",
        }
    )
    def get(self, request, *args, **kwargs):
        casher_id = request.query_params.get('casher_id')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        if not casher_id:
            return Response({'error': 'Casher ID is required'}, status=400)

        # Base filter
        filters = {"casher_id": casher_id}
        if start_date:
            filters["created_at__gte"] = start_date
        if end_date:
            filters["created_at__lte"] = end_date

        # Payment methods
        payment_methods = ['Click', 'Payme', 'Cash', 'Card', 'Money_send']

        # Aggregating income and expense per payment method
        data = {"Casher ID": casher_id}

        for method in payment_methods:
            income = \
                Finance.objects.filter(payment_method=method, action='INCOME', **filters).aggregate(
                    total=Sum('amount'))[
                    'total'] or 0
            expense = \
                Finance.objects.filter(payment_method=method, action='EXPENSE', **filters).aggregate(
                    total=Sum('amount'))[
                    'total'] or 0
            data[f"{method}_Income"] = income
            data[f"{method}_Expense"] = expense

        # Compute total income and expense
        data["Total_Income"] = sum(data[f"{p}_Income"] for p in payment_methods)
        data["Total_Expense"] = sum(data[f"{p}_Expense"] for p in payment_methods)

        # Create DataFrame
        df = pd.DataFrame([data])

        # Generate Excel file
        file_name = f"payment_casher_statistics_{now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename={file_name}'

        with pd.ExcelWriter(response, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Payment Statistics')

        return response
