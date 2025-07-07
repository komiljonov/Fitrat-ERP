from datetime import timedelta

import icecream
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.generics import ListCreateAPIView, ListAPIView, RetrieveUpdateDestroyAPIView, CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Archived
from .serializers import ArchivedSerializer, StuffArchivedSerializer
from ...account.models import CustomUser

from django.utils.dateparse import parse_datetime, parse_date
from datetime import timedelta

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
            queryset = queryset.filter(Q(student__call_operator__id=call_operator) | Q(lid__call_operator__id=call_operator))
        if sales_manager:
            queryset = queryset.filter(Q(student__sales_manager__id=sales_manager) | Q(lid__sales_manager__id=sales_manager))
        if service_manager:
            queryset = queryset.filter(Q(student__service_manager__id=service_manager) | Q(lid__service_manager__id=service_manager))

        if balance_from:
            queryset = queryset.filter(Q(student__balance__gte=balance_from) | Q(lid__balance__gte=balance_from))
        if balance_to:
            queryset = queryset.filter(Q(student__balance__lte=balance_to) | Q(lid__balance__lte=balance_to))

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













