import icecream
from django.db.models import Sum, Q
from django.utils.dateparse import parse_datetime
from django_filters.rest_framework import DjangoFilterBackend
from icecream import ic
from rest_framework import status
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.generics import ListAPIView, ListCreateAPIView, RetrieveUpdateDestroyAPIView, CreateAPIView, \
    RetrieveAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from data.account.models import CustomUser
from data.student.student.models import Student
from .models import Finance, Casher, Handover
from .serializers import FinanceSerializer, CasherSerializer, CasherHandoverSerializer, FinanceTeacherSerializer
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
        id = self.request.query_params.get('casher_id', None)
        finance = Finance.objects.filter(casher__id=id)
        if finance:
            return finance
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

    filter_backends = (DjangoFilterBackend,SearchFilter,OrderingFilter)
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
    def get_queryset(self,**kwargs):
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
            # Deduct from sender (casher)
            Finance.objects.create(
                casher=casher,
                amount=amount,
                action='EXPENSE',
                kind="CASHIER_HANDOVER",
                creator=request.user,
                comment=f"{casher.user.first_name} handed over {amount} "
                        f"to {receiver.user.first_name}"
            )

            # Add to receiver
            Finance.objects.create(
                casher=receiver,
                amount=amount,
                action='INCOME',
                kind="CASHIER_ACCEPTANCE",
                creator=request.user,
                comment=f"{receiver.user.first_name} received {amount}"
                        f" from {casher.user.first_name}"
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
        # Asosiy kassa balansi
        main_casher_income = Finance.objects.filter(casher__role="WEALTH", action="INCOME").aggregate(Sum("amount"))["amount__sum"] or 0
        main_casher_outcome = Finance.objects.filter(casher__role="WEALTH", action="OUTCOME").aggregate(Sum("amount"))["amount__sum"] or 0
        main_casher_balance = main_casher_income - main_casher_outcome

        # Administrativ kassa balansi
        admin_casher_income = Finance.objects.filter(casher__role="ADMINISTRATOR", action="INCOME").aggregate(Sum("amount"))["amount__sum"] or 0
        admin_casher_outcome = Finance.objects.filter(casher__role="ADMINISTRATOR", action="OUTCOME").aggregate(Sum("amount"))["amount__sum"] or 0
        admin_casher_balance = admin_casher_income - admin_casher_outcome

        # Accountant kassa balansi
        accounting_casher_income = Finance.objects.filter(casher__role="ACCOUNTANT", action="INCOME").aggregate(Sum("amount"))["amount__sum"] or 0
        accounting_casher_outcome = Finance.objects.filter(casher__role="ACCOUNTANT", action="OUTCOME").aggregate(Sum("amount"))["amount__sum"] or 0
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
    def get_queryset(self,**kwargs):
        casher = self.kwargs.get('pk')
        if casher:
            return Handover.objects.filter(casher__id=casher)
        return Finance.objects.none()

class CasherStatisticsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        casher = self.kwargs.get('pk')
        if casher:
            income = Finance.objects.filter(casher__id=casher, action='INCOME'
                                            ).aggregate(Sum('amount'))['amount__sum'] or 0
            expense = Finance.objects.filter(casher__id=casher, action='EXPENSE'
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
                student_attendances = Attendance.objects.filter(group_id=group_id, student=student).order_by("created_at")

                student_finance_filters = {"attendance__in": student_attendances}

                if start_date and end_date:
                    student_finance_filters["created_at__range"] = (start_date, end_date)
                elif start_date:
                    student_finance_filters["created_at__gte"] = start_date

                if student_attendances.exists():
                    first_attendance = student_attendances.first()
                    student_finance_filters["created_at__date"] = first_attendance.created_at.date()
                    total_student_payment = Finance.objects.filter(**student_finance_filters).aggregate(Sum('amount'))['amount__sum'] or 0
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
