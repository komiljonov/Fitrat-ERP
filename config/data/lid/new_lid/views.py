from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.generics import RetrieveUpdateDestroyAPIView, ListAPIView, \
    ListCreateAPIView, CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Lid
from ..new_lid.serializers import LidSerializer


class LidListCreateView(ListCreateAPIView):
    serializer_class = LidSerializer
    # queryset = Lid.objects.all()
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
        Return Lids that are not archived and belong to the requested user (call_operator)
        or have no assigned call_operator (None).
        """
        user = self.request.user
        # If the user is anonymous, return an empty queryset
        if user.is_anonymous:
            return Lid.objects.none()

        # Filter Lids that are not archived and have call_operator as the user or None
        return Lid.objects.filter(
            Q(is_archived=False) & (Q(call_operator=user) | Q(call_operator__isnull=True))
        )


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



class FirstLessonCreate(CreateAPIView):
    serializer_class = LidSerializer
    queryset = Lid.objects.all()
    permission_classes = [IsAuthenticated]


