from django.shortcuts import render
from rest_framework.generics import ListCreateAPIView,ListAPIView,RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import MarketingChannel
from .serializers import MarketingChannelSerializer


class MarketingChannelList(ListCreateAPIView):
    queryset = MarketingChannel.objects.all()
    serializer_class = MarketingChannelSerializer
    permission_classes = [IsAuthenticated]


class MarketingChannelDetail(RetrieveUpdateDestroyAPIView):
    queryset = MarketingChannel.objects.all()
    serializer_class = MarketingChannelSerializer
    permission_classes = [IsAuthenticated]

class MarketingChannelNOPG(ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = MarketingChannel.objects.all()
    serializer_class = MarketingChannelSerializer

    def get_paginated_response(self, data):
        return Response(data)
