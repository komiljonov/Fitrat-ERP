from django.db.models import Q
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Filial
from .serializers import FilialSerializer, UserFilialSerializer
from ...command.models import UserFilial


class FilialListCreate(ListCreateAPIView):
    queryset = Filial.objects.all()
    serializer_class = FilialSerializer
    permission_classes = [IsAuthenticated]


class FilialRetrieveUpdateDestroy(RetrieveUpdateDestroyAPIView):
    queryset = Filial.objects.all()
    serializer_class = FilialSerializer
    permission_classes = [IsAuthenticated]


class FilialListNoPG(ListAPIView):
    queryset = Filial.objects.all()
    serializer_class = FilialSerializer
    permission_classes = [IsAuthenticated]

    def get_paginated_response(self, data):
        return Response(data)


class UserFilialListCreate(ListCreateAPIView):
    queryset = UserFilial.objects.all()
    serializer_class = UserFilialSerializer

    def get_queryset(self):
        queryset = UserFilial.objects.all()

        is_archived = self.request.GET.get('is_archived')
        filial = self.request.GET.get('filial')
        search = self.request.GET.get('search')

        if search:
            queryset = queryset.filter(Q(user__first_name__icontains=search) | Q(user__last_name__icontains=search)
                                       | Q(filial__name__icontains=search)
                                       )
        if filial:
            queryset = queryset.filter(filial__id=filial)
        if is_archived:
            queryset = queryset.filter(is_archived=is_archived.capitalize())

        return queryset


class UserFilialRetrieveUpdateDestroy(RetrieveUpdateDestroyAPIView):
    queryset = UserFilial.objects.all()
    serializer_class = UserFilialSerializer
