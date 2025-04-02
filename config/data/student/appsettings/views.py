from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated

from .serializers import StoresSerializer
from .models import Store

from rest_framework.generics import ListCreateAPIView,RetrieveUpdateDestroyAPIView


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

