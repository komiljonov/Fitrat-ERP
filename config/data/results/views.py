from django.shortcuts import render
from rest_framework.generics import ListAPIView, ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

# Create your views here.
from .serializers import UniversityResultsSerializer, CertificationResultsSerializer, StudentResultsSerializer

from .models import Results

class UniversityResultsViewSet(ListCreateAPIView):
    queryset = Results.objects.all()
    serializer_class = UniversityResultsSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Results.objects.filter(teacher=self.request.user)

class CertificationResultsViewSet(ListCreateAPIView):
    queryset = Results.objects.all()
    serializer_class = CertificationResultsSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Results.objects.filter(teacher=self.request.user)

class UniversityResultsRetrieveAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Results.objects.all()
    serializer_class = UniversityResultsSerializer
    permission_classes = [IsAuthenticated]

class CertificationResultsRetrieveAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Results.objects.all()
    serializer_class = CertificationResultsSerializer
    permission_classes = [IsAuthenticated]


class UniversityResultsNoPg(ListAPIView):
    queryset = Results.objects.all()
    serializer_class = UniversityResultsSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Results.objects.filter(teacher=self.request.user)

    def get_paginated_response(self, data):
        return Response(data)

class CertificationResultsNoPg(ListAPIView):
    queryset = Results.objects.all()
    serializer_class = CertificationResultsSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Results.objects.filter(teacher=self.request.user)

    def get_paginated_response(self, data):
        return Response(data)


class ResultsViewSet(ListAPIView):
    queryset = Results.objects.all()
    serializer_class = StudentResultsSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Results.objects.filter(teacher=self.request.user)
