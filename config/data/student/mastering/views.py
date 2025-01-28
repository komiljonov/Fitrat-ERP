from django.shortcuts import render

from rest_framework.generics import ListAPIView,ListCreateAPIView,RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

# Create your views here.
from .serializers import MasteringSerializer
from .models import Mastering


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

