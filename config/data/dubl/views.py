from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Dubl
from .serializers import DublSerializer

from rest_framework.generics import (ListAPIView,
                                     ListCreateAPIView,
                                     RetrieveUpdateDestroyAPIView)

class DublListAPIView(ListCreateAPIView):
    queryset = Dubl.objects.all()
    serializer_class = DublSerializer
    permission_classes = (IsAuthenticated,)

class DublRetrieveAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Dubl.objects.all()
    serializer_class = DublSerializer
    permission_classes = (IsAuthenticated,)

class DublListNoPGView(ListAPIView):
    queryset = Dubl.objects.all()
    serializer_class = DublSerializer
    permission_classes = (IsAuthenticated,)

    def get_paginated_response(self, data):
        return Response(data)