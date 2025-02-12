from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated

from .models import Bonus, Compensation, Page
from .serializers import BonusSerializer, CompensationSerializer, PagesSerializer


class BonusList(ListCreateAPIView):
    queryset = Bonus.objects.all()
    serializer_class = BonusSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    search_fields = ("name",)
    filterset_fields = ("name",)
    ordering_fields = ("name",)

    def create(self, request, *args, **kwargs):
        if isinstance(request.data, list):
            serializer = self.get_serializer(data=request.data, many=True)  # Use `many=True`
        else:
            serializer = self.get_serializer(data=request.data)

        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class BonusDetail(RetrieveUpdateDestroyAPIView):
    queryset = Bonus.objects.all()
    serializer_class = BonusSerializer
    permission_classes = [IsAuthenticated]

class BonusNoPG(ListAPIView):
    queryset = Bonus.objects.all()
    serializer_class = BonusSerializer
    permission_classes = [IsAuthenticated]

    filter_backends = (DjangoFilterBackend,SearchFilter,OrderingFilter)
    search_fields = ("name",)
    filterset_fields = ("name",)
    ordering_fields = ("name",)


    def get_paginated_response(self, data):
        return Response(data)


class CompensationList(ListCreateAPIView):
    queryset = Compensation.objects.all()
    serializer_class = CompensationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    search_fields = ("name",)
    filterset_fields = ("name",)
    ordering_fields = ("name",)

    def create(self, request, *args, **kwargs):
        if isinstance(request.data, list):
            serializer = self.get_serializer(data=request.data, many=True)  # Use `many=True`
        else:
            serializer = self.get_serializer(data=request.data)

        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class CompensationDetail(RetrieveUpdateDestroyAPIView):
    queryset = Compensation.objects.all()
    serializer_class = CompensationSerializer

class CompensationNoPG(ListAPIView):
    queryset = Compensation.objects.all()
    serializer_class = CompensationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    search_fields = ("name",)
    filterset_fields = ("name",)
    ordering_fields = ("name",)

    def get_paginated_response(self, data):
        return Response(data)



class PageCreateView(ListCreateAPIView):
    queryset = Page.objects.all()
    serializer_class = PagesSerializer

    def create(self, request, *args, **kwargs):
        # Check if request data is a list
        if isinstance(request.data, list):
            serializer = self.get_serializer(data=request.data, many=True)  # Use `many=True`
        else:
            serializer = self.get_serializer(data=request.data)

        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get_paginated_response(self, data):
        return Response(data)


import json
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny


class FilterJSONData(ListAPIView):
    permission_classes = [AllowAny]

    def get_queryset(self):
        # Load JSON data from file
        with open("your_file.json", "r", encoding="utf-8") as file:
            json_data = json.load(file)

        # Get filtering parameters from request
        is_editable = self.request.query_params.get("is_editable")
        is_readable = self.request.query_params.get("is_readable")

        def filter_json(data):
            """Recursively filter nested JSON data."""
            filtered_data = {}

            for key, value in data.items():
                if isinstance(value, dict):
                    if "is_editable" in value and "is_readable" in value:
                        conditions_met = True
                        if is_editable is not None:
                            conditions_met &= value["is_editable"] == (is_editable.lower() == "true")
                        if is_readable is not None:
                            conditions_met &= value["is_readable"] == (is_readable.lower() == "true")

                        if conditions_met:
                            filtered_data[key] = value
                    else:
                        nested_result = filter_json(value)
                        if nested_result:
                            filtered_data[key] = nested_result

            return filtered_data

        filtered_result = filter_json(json_data)
        return filtered_result

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        return Response(queryset)
