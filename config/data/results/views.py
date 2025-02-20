from django.shortcuts import render
from rest_framework.generics import ListAPIView, ListCreateAPIView, RetrieveUpdateDestroyAPIView, CreateAPIView, \
    RetrieveUpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

# Create your views here.
from .serializers import UniversityResultsSerializer, CertificationResultsSerializer, StudentResultsSerializer, \
    OtherResultsSerializer, ResultsSerializer

from .models import Results

class UniversityResultsViewSet(ListCreateAPIView):
    queryset = Results.objects.all()
    serializer_class = UniversityResultsSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Results.objects.filter(teacher=self.request.user)
        status = self.request.query_params.get('status')
        if status:
            queryset = queryset.filter(status=status)
        certification_type = self.request.query_params.get('certificate_type')
        if certification_type:
            queryset = queryset.filter(certificate_type=certification_type)
        return queryset



class CertificationResultsViewSet(ListCreateAPIView):
    queryset = Results.objects.all()
    serializer_class = CertificationResultsSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Results.objects.filter(teacher=self.request.user)
        status = self.request.query_params.get('status')
        if status:
            queryset = queryset.filter(status=status)
        certification_type = self.request.query_params.get('certificate_type')
        if certification_type:
            queryset = queryset.filter(certificate_type=certification_type)
        return queryset

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
        queryset = Results.objects.filter(teacher=self.request.user)
        status = self.request.query_params.get('status')
        if status:
            queryset = queryset.filter(status=status)
        certification_type = self.request.query_params.get('certificate_type')
        if certification_type:
            queryset = queryset.filter(certificate_type=certification_type)
        return queryset

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
        queryset = Results.objects.filter(teacher=self.request.user)
        status = self.request.query_params.get('status')
        if status:
            queryset = queryset.filter(status=status)
        certification_type = self.request.query_params.get('certificate_type')
        if certification_type:
            queryset = queryset.filter(certificate_type=certification_type)
        if certification_type and status:
            queryset = queryset.filter(status=status, certificate_type=certification_type)
        return queryset



class OtherResultsViewSet(CreateAPIView):
    queryset = Results.objects.all()
    serializer_class = OtherResultsSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Results.objects.filter(teacher=self.request.user)
        status = self.request.query_params.get('status')
        if status:
            queryset = queryset.filter(status=status)
        certification_type = self.request.query_params.get('certificate_type')
        if certification_type:
            queryset = queryset.filter(certificate_type=certification_type)
        return queryset

    def get_paginated_response(self, data):
        return Response(data)

class OtherResultsRetrieveAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Results.objects.all()
    serializer_class = OtherResultsSerializer
    permission_classes = [IsAuthenticated]


class ResultsView(ListAPIView):
    queryset = Results.objects.all()
    serializer_class = ResultsSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        queryset = Results.objects.filter(filial=self.request.user.filial)
        status = self.request.query_params.get('status')
        type = self.request.query_params.get('type')

        if status:
            queryset = queryset.filter(status=status)
        if type:
            queryset = queryset.filter(results=type)
        return queryset

class ResultsRetrieveAPIView(RetrieveUpdateAPIView):
    queryset = Results.objects.all()
    serializer_class = ResultsSerializer
    permission_classes = [IsAuthenticated]
