from django.db.models import Avg, OuterRef, Subquery, Prefetch
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, ListAPIView, RetrieveAPIView, \
    CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from .models import Bonus, Compensation, Page, Asos, Monitoring, Point
from .serializers import BonusSerializer, CompensationSerializer, PagesSerializer, AsosSerializer, MonitoringSerializer, \
    PointSerializer

import json
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from ...account.models import CustomUser


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


class PageBulkUpdateView(APIView):
    def put(self, request, *args, **kwargs):
        # Ensure the request body is a list of pages with ids and updated data
        if isinstance(request.data, list):
            updated_pages = []
            for data in request.data:
                try:
                    # Find the Page object to update
                    page = Page.objects.get(id=data['id'])

                    # If the 'user' field is provided, get the CustomUser instance
                    if 'user' in data:
                        try:
                            user_instance = CustomUser.objects.get(id=data['user'])
                            data['user'] = user_instance  # Assign the CustomUser instance
                        except CustomUser.DoesNotExist:
                            return Response({"detail": f"CustomUser with id {data['user']} does not exist."},
                                            status=status.HTTP_400_BAD_REQUEST)

                    # Update each field
                    for attr, value in data.items():
                        setattr(page, attr, value)
                    updated_pages.append(page)
                except Page.DoesNotExist:
                    # Handle if the Page with the given ID doesn't exist
                    continue

            # Perform bulk update (only if there are pages to update)
            if updated_pages:
                Page.objects.bulk_update(updated_pages,
                                         fields=['name', 'user', 'is_editable', 'is_readable', 'is_parent'])

            return Response(
                {"updated_pages": PagesSerializer(updated_pages, many=True).data},
                status=status.HTTP_200_OK
            )

        return Response({"detail": "Expected a list of pages for update."}, status=status.HTTP_400_BAD_REQUEST)


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


class AsosListCreateView(ListCreateAPIView):
    queryset = Asos.objects.all()
    serializer_class = AsosSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        filial = self.request.query_params.get("filial")
        queryset = Asos.objects.all()
        if filial:
            queryset = queryset.filter(filial__id=filial)
        return queryset

class AsosListRetrieveView(RetrieveUpdateDestroyAPIView):
    queryset = Asos.objects.all()
    serializer_class = AsosSerializer
    permission_classes = [IsAuthenticated]


class AsosNoPGListView(ListAPIView):
    queryset = Asos.objects.all()
    serializer_class = AsosSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        filial = self.request.query_params.get("filial")
        queryset = Asos.objects.all()
        if filial:
            queryset = queryset.filter(filial__id=filial)
        return queryset

    def get_paginated_response(self, data):
        return Response(data)


class PointListCreateView(ListCreateAPIView):
    queryset = Point.objects.all()
    serializer_class = PointSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        user = request.user  # Get the authenticated user
        user_filial = getattr(user, "filial", None)  # Get user's filial (if available)

        data = request.data.copy()  # Copy request data to modify it
        if "filial" not in data:  # If filial is not provided, use user's filial
            data["filial"] = user_filial.first().id if user_filial else None

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get_queryset(self):
        asos = self.request.query_params.get("asos")
        filial = self.request.query_params.get("filial")

        queryset = Point.objects.all()
        if asos:
            queryset = queryset.filter(asos__id=asos)
        if filial:
            queryset = queryset.filter(filial__id=filial)
        return queryset


class PointRetrieveView(RetrieveUpdateDestroyAPIView):
    queryset = Point.objects.all()
    serializer_class = PointSerializer
    permission_classes = [IsAuthenticated]


class PointNoPGListView(ListAPIView):
    queryset = Point.objects.all()
    serializer_class = PointSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        asos = self.request.query_params.get("asos")
        filial = self.request.query_params.get("filial")
        user = self.request.query_params.get("user")

        start_date = self.request.query_params.get("start_date")
        end_date = self.request.query_params.get("end_date")

        queryset = Point.objects.all()
        if start_date:
            queryset = queryset.filter(craeted_at__gte=start_date)
        if start_date and end_date:
            queryset = queryset.filter(craeted_at__gte=start_date, craeted_at__lte=end_date)
        if asos:
            queryset = queryset.filter(asos__id=asos)
        if filial:
            queryset = queryset.filter(filial__id=filial)

        # Only filter by user if provided
        if user:
            queryset = queryset.filter(point_monitoring__user_id=user)

            # Subquery to get the user's average `ball` for each point
            monitoring_avg_subquery = Monitoring.objects.filter(
                point=OuterRef('id'),
                user_id=user
            ).values("point").annotate(avg_ball=Avg("ball")).values("avg_ball")

            queryset = queryset.annotate(user_avg_ball=Subquery(monitoring_avg_subquery))

            # Prefetch only the monitoring records related to this user for each point
            user_monitoring_qs = Monitoring.objects.filter(user_id=user)
            queryset = queryset.prefetch_related(
                Prefetch("point_monitoring", queryset=user_monitoring_qs,
                         to_attr="user_monitorings")
            )

        return queryset

    def get_paginated_response(self, data):
        return Response(data)


class MonitoringListCreateView(ListAPIView):
    queryset = Monitoring.objects.all()
    serializer_class = MonitoringSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        filial = self.request.query_params.get("filial")
        point = self.request.query_params.get("point")
        user = self.request.query_params.get("user")
        queryset = Monitoring.objects.all()
        if user:
            queryset = queryset.filter(user__id=user)
        if point:
            queryset = queryset.filter(point__id=point)
        if filial:
            queryset = queryset.filter(filial__id=filial)

        return queryset


class MonitoringRetrieveView(RetrieveUpdateDestroyAPIView):
    queryset = Monitoring.objects.all()
    serializer_class = MonitoringSerializer
    permission_classes = [IsAuthenticated]


class MonitoringBulkCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = MonitoringSerializer(data=request.data, many=True,
                        context={'request': request})
        serializer.is_valid(raise_exception=True)
        instances = serializer.save()

        return Response(MonitoringSerializer(instances, many=True).data,
                        status=status.HTTP_201_CREATED)


