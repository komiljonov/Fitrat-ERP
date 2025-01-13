from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .serializers import NewLidStageSerializer, StudentStagesSerializer, NewOrderedLidStagesSerializer
from .models import NewLidStages, NewStudentStages, NewOredersStages


class NewLidStagesViewSet(ListCreateAPIView):
    queryset = NewLidStages.objects.all()
    serializer_class = NewLidStageSerializer
    permission_classes = [IsAuthenticated]


class NewLidStagesRetrive(RetrieveUpdateDestroyAPIView):
    queryset = NewLidStages.objects.all()
    serializer_class = NewLidStageSerializer
    permission_classes = [IsAuthenticated]

class NewLidNoPG(ListAPIView):
    queryset = NewLidStages.objects.all()
    serializer_class = NewLidStageSerializer
    permission_classes = [IsAuthenticated]

    def get_paginated_response(self, data):
        return Response(data)


class NewOrderedLidListView(ListCreateAPIView):
    queryset = NewLidStages.objects.all()
    serializer_class = NewLidStageSerializer
    permission_classes = [IsAuthenticated]

class NewOrederedRetriveView(RetrieveUpdateDestroyAPIView):
    queryset = NewLidStages.objects.all()
    serializer_class = NewOrderedLidStagesSerializer
    permission_classes = [IsAuthenticated]


class NewOrederedNOPgListView(ListAPIView):
    queryset = NewLidStages.objects.all()
    serializer_class = NewOrderedLidStagesSerializer

