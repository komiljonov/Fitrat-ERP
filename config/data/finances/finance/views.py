import icecream
import pandas as pd
from django.db.models import Sum
from django.http import HttpResponse
from django.utils.dateparse import parse_datetime
from django_filters.rest_framework import DjangoFilterBackend
from icecream import ic
from pandas import io
from rest_framework import status
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.generics import ListAPIView, ListCreateAPIView, RetrieveUpdateDestroyAPIView, CreateAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from data.account.models import CustomUser
from data.student.student.models import Student
from .models import Finance, Casher, Handover, Kind, PaymentMethod
from .serializers import FinanceSerializer, CasherSerializer, CasherHandoverSerializer, KindSerializer, \
    PaymentMethodSerializer
from ...lid.new_lid.models import Lid
from ...student.attendance.models import Attendance


class CasherListCreateAPIView(ListCreateAPIView):
    queryset = Casher.objects.all()
    serializer_class = CasherSerializer
    permission_classes = [IsAuthenticated]


class CasherRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Casher.objects.all()
    serializer_class = CasherSerializer
    permission_classes = [IsAuthenticated]


class CasherNoPg(ListAPIView):
    queryset = Casher.objects.all()
    serializer_class = CasherSerializer
    permission_classes = [IsAuthenticated]

    def get_paginated_response(self, data):
        return Response(data)


class FinanceListAPIView(ListCreateAPIView):
    queryset = Finance.objects.all()
    serializer_class = FinanceSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        kind = self.request.query_params.get('kind', None)
        id = self.request.query_params.get('casher_id', None)
        finance = Finance.objects.filter(casher__id=id)
        if finance:
            return finance
        if kind:
            return Finance.objects.filter(kind=Kind.objects.get(id=kind))
        if kind and id:
            return Finance.objects.filter(casher__id=id, kind=Kind.objects.get(id=kind))
        return Finance.objects.none()


class FinanceDetailAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Finance.objects.all()
    serializer_class = FinanceSerializer
    permission_classes = (IsAuthenticated,)


class FinanceNoPGList(ListAPIView):
    queryset = Finance.objects.all()
    serializer_class = FinanceSerializer
    permission_classes = (IsAuthenticated,)

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
        stuff = CustomUser.objects.get(id=self.kwargs['pk'])
        if stuff:
            return Finance.objects.filter(stuff=stuff)
        return Finance.objects.none()


class CasherHandoverAPIView(CreateAPIView):
    serializer_class = CasherHandoverSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        receiver = serializer.validated_data.get("receiver")
        casher = serializer.validated_data.get("casher")
        amount = serializer.validated_data.get("amount")
        icecream.ic(receiver, casher, amount)

        if int(amount) > 0:
            # Get the Kind instance (unpacking the tuple)
            handover, _ = Kind.objects.get_or_create(name="CASHIER_HANDOVER", action="EXPENSE")

            # Deduct from sender (casher)
            Finance.objects.create(
                casher=casher,
                amount=amount,
                action='EXPENSE',
                kind=handover,  # Now it's correctly assigned
                creator=request.user,
                comment=f"{casher.user.first_name} handed over {amount} "
                        f"to {receiver.user.first_name}"
            )

            # Get the Kind instance (unpacking the tuple)
            acception, _ = Kind.objects.get_or_create(name="CASHIER_ACCEPTANCE", action="INCOME")

            # Add to receiver
            Finance.objects.create(
                casher=receiver,
                amount=amount,
                action='INCOME',
                kind=acception,  # Now it's correctly assigned
                creator=request.user,
                comment=f"{receiver.user.first_name} received {amount} "
                        f"from {casher.user.first_name}"
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
    permission_classes = [IsAuthenticated]

    def get(self, request):
        kind = self.request.query_params.get('kind', None)
        filter = {}
        if kind:
            filter['kind'] = Kind.objects.get(id=kind)
        # Asosiy kassa balansi
        main_casher_income = \
        Finance.objects.filter(casher__role="WEALTH", action="INCOME", **filter).aggregate(Sum("amount"))[
            "amount__sum"] or 0
        main_casher_outcome = \
        Finance.objects.filter(casher__role="WEALTH", action="OUTCOME", **filter).aggregate(Sum("amount"))[
            "amount__sum"] or 0
        main_casher_balance = main_casher_income - main_casher_outcome

        # Administrativ kassa balansi
        admin_casher_income = \
        Finance.objects.filter(casher__role="ADMINISTRATOR", action="INCOME", **filter).aggregate(Sum("amount"))[
            "amount__sum"] or 0
        admin_casher_outcome = \
        Finance.objects.filter(casher__role="ADMINISTRATOR", action="OUTCOME", **filter).aggregate(Sum("amount"))[
            "amount__sum"] or 0
        admin_casher_balance = admin_casher_income - admin_casher_outcome

        # Accountant kassa balansi
        accounting_casher_income = \
        Finance.objects.filter(casher__role="ACCOUNTANT", action="INCOME", **filter).aggregate(Sum("amount"))[
            "amount__sum"] or 0
        accounting_casher_outcome = \
        Finance.objects.filter(casher__role="ACCOUNTANT", action="OUTCOME", **filter).aggregate(Sum("amount"))[
            "amount__sum"] or 0
        accounting_casher_balance = accounting_casher_income - accounting_casher_outcome

        # JSON response qaytarish
        return Response({
            "main_casher": main_casher_balance,
            "admin_casher": admin_casher_balance,
            "accounting_casher": accounting_casher_balance,
        })


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
        casher = self.kwargs.get('pk')
        kind = self.request.query_params.get('kind', None)
        filter = {}
        if kind:
            filter['kind'] = Kind.objects.get(id=kind)
        if casher:
            income = Finance.objects.filter(casher__id=casher, action='INCOME', **filter
                                            ).aggregate(Sum('amount'))['amount__sum'] or 0
            expense = Finance.objects.filter(casher__id=casher, action='EXPENSE', **filter
                                             ).aggregate(Sum('amount'))['amount__sum'] or 0
            balance = income - expense
            return Response({
                "income": income,
                "expense": expense,
                "balance": balance,
            })
        return Response({"error": "Casher not found"}, status=404)


class CustomPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class TeacherGroupFinanceAPIView(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination  # Attach custom pagination

    def get(self, request, *args, **kwargs):
        teacher_id = self.kwargs.get('pk')  # Get teacher ID from URL parameter
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')

        # Get attended groups for the teacher
        group_filters = {"group__teacher_id": teacher_id}

        if start_date and end_date:
            group_filters["created_at__range"] = (start_date, end_date)  # Use range filter
        elif start_date:
            group_filters["created_at__gte"] = start_date

        attended_groups = Attendance.objects.filter(**group_filters).values_list('group_id', flat=True).distinct()

        # Use a list to store unique group data for pagination
        group_data_list = []

        for group_id in attended_groups:
            # Apply start_date and end_date filters dynamically
            finance_filters = {"attendance__group__id": group_id}

            if start_date and end_date:
                finance_filters["created_at__range"] = (start_date, end_date)
            elif start_date:
                finance_filters["created_at__gte"] = start_date

            # Fetch finance records sorted by group and date
            finance_records = Finance.objects.filter(**finance_filters).order_by("created_at")

            if finance_records.exists():
                created_at = finance_records.first().created_at
            else:
                created_at = None

            # Sum total payments for the group on each date
            total_group_payment = finance_records.aggregate(Sum('amount'))['amount__sum'] or 0
            ic(total_group_payment)

            # Get distinct students per group
            student_data = []
            students = Student.objects.filter(attendance__group_id=group_id).distinct()
            ic(students)

            for student in students:
                student_attendances = Attendance.objects.filter(group_id=group_id, student=student).order_by(
                    "created_at")

                student_finance_filters = {"attendance__in": student_attendances}

                if start_date and end_date:
                    student_finance_filters["created_at__range"] = (start_date, end_date)
                elif start_date:
                    student_finance_filters["created_at__gte"] = start_date

                if student_attendances.exists():
                    first_attendance = student_attendances.first()
                    student_finance_filters["created_at__date"] = first_attendance.created_at.date()
                    total_student_payment = Finance.objects.filter(**student_finance_filters).aggregate(Sum('amount'))[
                                                'amount__sum'] or 0
                else:
                    total_student_payment = 0

                student_data.append({
                    "student_id": str(student.id),
                    "student_name": f"{student.first_name} {student.last_name}",
                    "total_payment": total_student_payment
                })

            # Get group name safely
            group_name = Attendance.objects.filter(group_id=group_id).first()
            group_name = group_name.group.name if group_name else "Unknown Group"

            # Append group data to list
            group_data_list.append({
                "group_id": str(group_id),
                "group_name": group_name,
                "total_group_payment": total_group_payment,
                "students": student_data,
                "created_at": created_at,
            })

        # 🔹 Apply Pagination
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
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        casher_id = request.query_params.get('casher')
        action = request.query_params.get('action')  # INCOME / EXPENSE
        kind = request.query_params.get('kind')  # COURSE_PAYMENT, LESSON_PAYMENT, etc.

        # Base queryset
        finance_queryset = Finance.objects.all()

        # Apply casher filter if provided
        if casher_id:
            finance_queryset = finance_queryset.filter(casher_id=casher_id)

        # Apply action filter if provided
        if action:
            finance_queryset = finance_queryset.filter(action=action.upper())

        # Apply kind filter if provided
        if kind:
            finance_queryset = finance_queryset.filter(kind=kind.upper())

        # Convert queryset to a list of dictionaries
        finance_data = list(finance_queryset.values(
            'casher__user__phone', 'action', 'amount', 'kind',
            'student__first_name', 'student__last_name',
            'stuff__phone', 'creator__phone',
            'comment', 'created_at',
        ))

        # Convert to DataFrame
        df = pd.DataFrame(finance_data)

        # Rename columns for readability
        df.rename(columns={
            'casher__user__phone': 'Kassa egasi raqami',
            'action': 'Action turi',
            'amount': 'Qiymat',
            'kind': "To'lov turi",
            'student__first_name': "O'quvchining ismi",
            'student__last_name': "O'quvchining familiyasi",
            'stuff__phone': 'Xodim raqami',
            'creator__phone': "To'lov qabul qiluvchining raqami",
            'comment': 'Comment',
            'created_at': 'Yaratilgan vaqti',
        }, inplace=True)

        # Convert DataFrame to Excel
        excel_buffer = io.BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Finance Data')

        # Prepare response
        response = HttpResponse(
            excel_buffer.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename="finance_data.xlsx"'
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


class KindRetrive(RetrieveUpdateDestroyAPIView):
    serializer_class = KindSerializer
    permission_classes = [IsAuthenticated]
    queryset = Kind.objects.all()


class PaymentMethodsList(ListCreateAPIView):
    queryset = PaymentMethod.objects.all()
    serializer_class = PaymentMethodSerializer
    permission_classes = [IsAuthenticated]


class PaymentMethodsRetrive(RetrieveUpdateDestroyAPIView):
    serializer_class = PaymentMethodSerializer
    permission_classes = [IsAuthenticated]
    queryset = PaymentMethod.objects.all()


class PaymentStatistics(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        filter = {}

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
        """Fetch and return payment statistics per cashier."""
        id = self.kwargs.get('pk')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        # Validate that `id` exists
        if not id:
            return Response({"error": "Casher ID is required"}, status=400)

        # Define filters
        filter = {"casher__id": id}
        if start_date:
            filter['created_at__gte'] = start_date
        if end_date:
            filter['created_at__lte'] = end_date

        # Define valid payment methods
        valid_payment_methods = [
            'Click', 'Payme', 'Naqt pul', 'Card', "Pul o'tkazish"
        ]

        # Function to calculate totals
        def get_total_amount(payment, action_type):
            return Finance.objects.filter(payment_method=payment, action=action_type, **filter).aggregate(
                total=Sum('amount'))['total'] or 0

        # Compute income and expense for each method
        data = {}
        for payment in valid_payment_methods:
            formatted_name = payment.lower().replace(" ", "_")
            data[f"{formatted_name}_income"] = get_total_amount(payment, "INCOME")
            data[f"{formatted_name}_expense"] = get_total_amount(payment, "EXPENSE")

        # Compute total income and expense
        data["total_income"] = sum(data[f"{p.lower().replace(' ', '_')}_income"] for p in valid_payment_methods)
        data["total_expense"] = sum(data[f"{p.lower().replace(' ', '_')}_expense"] for p in valid_payment_methods)

        return Response(data)

    def get_queryset(self):
        """ListAPIView requires a queryset; returning an empty one to satisfy DRF behavior."""
        return Finance.objects.none()
