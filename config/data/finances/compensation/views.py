from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from rest_framework.generics import ListCreateAPIView,RetrieveUpdateDestroyAPIView,ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Bonus, Compensation, Page
from .serializers import BonusSerializer, CompensationSerializer, PagesSerializer


class BonusList(ListCreateAPIView):
    queryset = Bonus.objects.all()
    serializer_class = BonusSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    search_fields = ("name",)
    filterset_fields = ("name",)
    ordering_fields = ("name",)

class BonusDetail(RetrieveUpdateDestroyAPIView):
    queryset = Bonus.objects.all()
    serializer_class = BonusSerializer
    permission_classes = [IsAuthenticated]

class BonusNoPG(ListAPIView):
    queryset = Bonus.objects.all()
    serializer_class = BonusSerializer
    permission_classes = [IsAuthenticated]

    filter_backends = (DjangoFilterBackend,SearchFilter,OrderingFilter)
    search_fields = ("name",)
    filterset_fields = ("name",)
    ordering_fields = ("name",)


    def get_paginated_response(self, data):
        return Response(data)


class CompensationList(ListCreateAPIView):
    queryset = Compensation.objects.all()
    serializer_class = CompensationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    search_fields = ("name",)
    filterset_fields = ("name",)
    ordering_fields = ("name",)

class CompensationDetail(RetrieveUpdateDestroyAPIView):
    queryset = Compensation.objects.all()
    serializer_class = CompensationSerializer

class CompensationNoPG(ListAPIView):
    queryset = Compensation.objects.all()
    serializer_class = CompensationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    search_fields = ("name",)
    filterset_fields = ("name",)
    ordering_fields = ("name",)

    def get_paginated_response(self, data):
        return Response(data)



class PagesList(ListCreateAPIView):
    queryset = Page.objects.all()
    serializer_class = PagesSerializer
    permission_classes = [IsAuthenticated]

    def get_paginated_response(self, data):
        return Response(data)
