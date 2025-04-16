from django.shortcuts import render
from reportlab import Version
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from ...finances.finance.models import Finance
from ...notifications.models import Notification
from ...notifications.serializers import NotificationSerializer
from ...student.course.models import Course
from ...student.student.models import Student
from ...student.studentgroup.models import StudentGroup

from rest_framework.response import Response

from .serializers import StoresSerializer, StudentAPPSerializer, StudentFinanceSerializer, StrikeSerializer, \
    VersionUpdateSerializer
from .models import Store, Strike, VersionUpdate

from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
    ListAPIView
    )

class StoresListView(ListCreateAPIView):
    queryset = Store.objects.all()
    serializer_class = StoresSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Store.objects.all()

        filial = self.request.query_params.get('filial', None)

        seen = self.request.query_params.get('seen', None)
        if filial:
            queryset = queryset.filter(filial__id=filial)
        if seen:
            queryset = queryset.filter(seen=seen.capitalize())
        return queryset


class StoreDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Store.objects.all()
    serializer_class = StoresSerializer
    permission_classes = [IsAuthenticated]


class StudentDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentAPPSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'user__id'


class FinanceListView(ListAPIView):
    queryset = Finance.objects.all()
    serializer_class = StudentFinanceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        id = self.kwargs.get('id')

        action =  self.request.query_params.get('action', None)
        kind = self.request.query_params.get('kind', None)
        payment_method = self.request.query_params.get('payment_method', None)
        search = self.request.query_params.get('search', None)

        queryset = Finance.objects.all()
        if id:
            queryset = queryset.filter(student__id=id)

        if action:
            queryset = queryset.filter(action=action)

        if kind:
            queryset = queryset.filter(kind__id=kind)

        if payment_method:
            queryset = queryset.filter(payment_method=payment_method)

        if search:
            queryset = queryset.filter(amount__icontains=search)

        return queryset


class StrikeListView(ListCreateAPIView):
    queryset = Strike.objects.all()
    serializer_class = StrikeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        id = self.request.query_params.get('id', None)
        if id:
            return Strike.objects.filter(student__user__id=id)
        return Strike.objects.none()


class VersionUpdateView(ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = VersionUpdate.objects.all()
    serializer_class = VersionUpdateSerializer

    def get_queryset(self):
        app_name = self.request.query_params.get('app_name', None)
        if app_name:
            queryset = VersionUpdate.objects.filter(app_name=app_name).first()
            return queryset
        return VersionUpdate.objects.none()


class StudentNotificationsView(ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer

    def get_queryset(self):
        id = self.request.query_params.get('id', None)
        if id:
            return Notification.objects.filter(user__id=id)
        return Notification.objects.none()