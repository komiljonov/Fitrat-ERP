import icecream
from django.shortcuts import render

from rest_framework.generics import ListAPIView,ListCreateAPIView,RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

# Create your views here.
from .serializers import MasteringSerializer, StuffMasteringSerializer
from .models import Mastering, MasteringTeachers
from ...finances.finance.models import KpiFinance
from ...finances.finance.serializers import KpiFinanceSerializer


class MasteringList(ListCreateAPIView):
    queryset = Mastering.objects.all()
    serializer_class = MasteringSerializer
    permission_classes = [IsAuthenticated]

class MasteringDetail(RetrieveUpdateDestroyAPIView):
    queryset = Mastering.objects.all()
    serializer_class = MasteringSerializer
    permission_classes = [IsAuthenticated]


class MasteringNoPG(ListAPIView):
    queryset = Mastering.objects.all()
    serializer_class = MasteringSerializer
    permission_classes = [IsAuthenticated]

    def get_paginated_response(self, data):
        return Response(data)

class MasteringQuizFilter(ListAPIView):
    queryset = Mastering.objects.all()
    serializer_class = MasteringSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        quiz_id = self.kwargs.get('quiz_id')
        quiz = Mastering.objects.filter(test__id=quiz_id)
        if quiz:
            return quiz
        return Mastering.objects.none()

# class TeacherMasteringList(ListAPIView):
#     queryset = MasteringTeachers.objects.all()
#     serializer_class = StuffMasteringSerializer
#     permission_classes = [IsAuthenticated]
#
#     def get_queryset(self):
#         id = self.kwargs.get('pk')
#         icecream.ic(id)
#         if id:
#             return MasteringTeachers.objects.filter(teacher__id=id)
#         return MasteringTeachers.objects.none()
#
#
# class StuffMasteringList(ListCreateAPIView):
#     queryset = KpiFinance.objects.all()
#     serializer_class = KpiFinanceSerializer
#     permission_classes = [IsAuthenticated]
#
#     def get_queryset(self):
#         id = self.request.query_params.get('id')
#         if id:
#             return KpiFinance.objects.filter(user__id=id)
#         return KpiFinance.objects.all()
#
#
# class MasteringTeachersList(RetrieveUpdateDestroyAPIView):
#     queryset = KpiFinance.objects.all()
#     serializer_class = KpiFinanceSerializer
#     permission_classes = [IsAuthenticated]
#


class MasteringStudentFilter(ListAPIView):
    queryset = Mastering.objects.all()
    serializer_class = MasteringSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        quiz_id = self.request.query_qaram.get('quiz_id')
        student = self.request.query_param.get('student')
        user = self.queryset.query_param.get('user')
        queryset = Mastering.objects.all()
        if quiz_id:
            queryset = queryset.filter(test__id=quiz_id)

        if student:
            queryset = queryset.filter(student__id=student)

        if user:
            queryset = queryset.filter(student__user__id=user)
        return queryset
