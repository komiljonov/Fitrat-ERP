from rest_framework.generics import ListCreateAPIView,ListAPIView,RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Group_Type
from .models import MarketingChannel
from .serializers import Group_typeSerializer
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


class GroupTypeList(ListAPIView):
    queryset = Group_Type.objects.all()
    serializer_class = Group_typeSerializer
    permission_classes = [IsAuthenticated]

    def get_paginated_response(self, data):
        return Response(data)

class GroupTypeDetail(RetrieveUpdateDestroyAPIView):
    queryset = Group_Type.objects.all()
    serializer_class = Group_typeSerializer
    permission_classes = [IsAuthenticated]