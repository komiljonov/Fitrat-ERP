from django.shortcuts import render
from django.utils.dateparse import parse_datetime

from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import ListAPIView,ListCreateAPIView,RetrieveUpdateDestroyAPIView
from rest_framework.response import Response

from .models import Finance
from .serializers import FinanceSerializer
from data.account.models import CustomUser
from data.student.student.models import Student
from ...lid.new_lid.models import Lid


class FinanceListAPIView(ListCreateAPIView):
    queryset = Finance.objects.all()
    serializer_class = FinanceSerializer
    permission_classes = (IsAuthenticated,)

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

    def get_queryset(self, **kwargs):
        queryset = Finance.objects.all()

        pk = self.kwargs.get('pk')
        student = Student.objects.filter(id=pk).first()  # Safer query, no exception if not found
        lid = Lid.objects.filter(id=pk).first()  # Safer query for lid

        if student:
            queryset = queryset.filter(student=student)
        elif lid:
            queryset = queryset.filter(lid=lid)

        action = self.request.query_params.get('action')
        print(action)

        if action == 'INCOME':
            queryset = queryset.filter(action='INCOME')
        elif action == 'EXPENSE':
            queryset = queryset.filter(action='EXPENSE')

        # Filter by date range if provided
        start_date = self.request.query_params.get("start_date")
        end_date = self.request.query_params.get("end_date")

        if start_date and end_date:
            try:
                start_date = parse_datetime(start_date).date()
                end_date = parse_datetime(end_date).date()
                queryset = queryset.filter(created_at__range=[start_date, end_date])
            except ValueError:
                pass  # Handle invalid date format, if necessary
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


class StuffFinanceListAPIView(ListAPIView):
    queryset = Finance.objects.all()
    serializer_class = FinanceSerializer
    permission_classes = (IsAuthenticated,)
    def get_queryset(self,**kwargs):
        stuff = CustomUser.objects.get(id=self.kwargs['pk'])
        if stuff:
            return Finance.objects.filter(stuff=stuff)
        return Finance.objects.none()


