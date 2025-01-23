from django.shortcuts import render

from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import ListAPIView,ListCreateAPIView,RetrieveUpdateDestroyAPIView
from rest_framework.response import Response

from .models import Finance
from .serializers import FinanceSerializer
from data.account.models import CustomUser
from data.student.student.models import Student


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
    queryset = Finance.objects.all()
    serializer_class = FinanceSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self,**kwargs):
        student = Student.objects.get(id=self.kwargs['pk'])
        if student:
            return Finance.objects.filter(student=student)
        return Finance.objects.none()


class StuffFinanceListAPIView(ListAPIView):
    queryset = Finance.objects.all()
    serializer_class = FinanceSerializer
    permission_classes = (IsAuthenticated,)
    def get_queryset(self,**kwargs):
        stuff = CustomUser.objects.get(id=self.kwargs['pk'])
        if stuff:
            return Finance.objects.filter(stuff=stuff)
        return Finance.objects.none()


