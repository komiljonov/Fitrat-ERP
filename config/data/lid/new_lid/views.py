from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import request
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.generics import RetrieveUpdateDestroyAPIView, ListAPIView, \
    ListCreateAPIView, CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Lid
from ..new_lid.serializers import LidSerializer

class LidListCreateView(ListCreateAPIView):
    serializer_class = LidSerializer
    # permission_classes = [IsAuthenticated]
    filter_backends = (DjangoFilterBackend,SearchFilter,OrderingFilter)

    search_fields = (
        'first_name',
        'last_name',
        "phone_number",
        "student_type",
        "education_lang",
        "comment", "filial",
        "marketing_channel",
        "lid_stages",
        "ordered_stages",
        "is_archived",
        "is_dubl"
    )
    ordering_fields = (
        'first_name',
        'last_name',
        "phone_number",
        "student_type",
        "education_lang",
        "comment", "filial",
        "marketing_channel",
        "lid_stages",
        "ordered_stages",
        "is_dubl"
    )

    filterset_fields = (
        'first_name',
        'last_name',
        "phone_number",
        "student_type",
        "education_lang",
        "comment", "filial",
        "marketing_channel",
        "lid_stages",
        "ordered_stages",
        "is_dubl"
    )
    def get_queryset(self):
        """
        Return Lids that are not archived and belong to the requested user (call_operator).
        """
        user = self.request.user  # Get the current user from the request
        if user.is_anonymous:
            return Lid.objects.none()
        return Lid.objects.filter(is_archived=False, call_operator=user)


class LidRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    serializer_class = LidSerializer
    queryset = Lid.objects.all()
    permission_classes = [IsAuthenticated]


class LidListNoPG(ListAPIView):
    queryset = Lid.objects.all()
    serializer_class = LidSerializer
    permission_classes = [IsAuthenticated]
    def get_paginated_response(self, data):
        return Response(data)


