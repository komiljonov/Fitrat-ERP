import icecream
from django.db.models import Sum
from django.utils.dateparse import parse_datetime
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.generics import ListAPIView, ListCreateAPIView, RetrieveUpdateDestroyAPIView, CreateAPIView, \
    RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from data.account.models import CustomUser
from data.student.student.models import Student
from .models import Finance, Casher, Handover
from .serializers import FinanceSerializer, CasherSerializer, CasherHandoverSerializer
from ...lid.new_lid.models import Lid


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


class TeacherHandover(ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Finance.objects.all()
    serializer_class = FinanceSerializer
    def get_queryset(self,**kwargs):
        id = self.kwargs.get('pk')
        if id:
            user = CustomUser.objects.filter(id=id).first()
            if user:
                return Finance.objects.filter(stuff__id=id)
        return Finance.objects.none()

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

class CasherStatisticsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        casher = self.kwargs.get('pk')
        if casher:
            income = Finance.objects.filter(casher__id=casher, action='INCOME').aggregate(Sum('amount'))['amount__sum'] or 0
            expense = Finance.objects.filter(casher__id=casher, action='EXPENSE').aggregate(Sum('amount'))['amount__sum'] or 0
            balance = income - expense
            return Response({
                "income": income,
                "expense": expense,
                "balance": balance,
            })
        return Response({"error": "Casher not found"}, status=404)
