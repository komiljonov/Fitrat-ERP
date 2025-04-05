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


class ArchivedListAPIView(ListCreateAPIView):
    queryset = Archived.objects.all()
    serializer_class = ArchivedSerializer
    permission_classes = (IsAuthenticated,)

    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)

    search_fields = ('reason',)
    filterset_fields = ('reason',)
    ordering_fields = ('reason',)


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
