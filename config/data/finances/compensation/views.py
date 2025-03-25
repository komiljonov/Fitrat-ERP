import json

from django.db.models import Avg, OuterRef, Subquery, Prefetch, Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.generics import ListAPIView
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Bonus, Compensation, Page, Asos, Monitoring, Point, ResultSubjects, StudentCountMonitoring, \
    ResultName, MonitoringAsos4, Comments, Monitoring5
from .serializers import BonusSerializer, CompensationSerializer, PagesSerializer, AsosSerializer, MonitoringSerializer, \
    PointSerializer, ResultPointsSerializer, StudentCountMonitoringSerializer, ResultsNameSerializer, \
    MonitoringAsos4Serializer, CommentsSerializer, Monitoring5Serializer
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
        creator = self.request.query_params.get("creator")
        asos = self.request.query_params.get("asos")
        point = self.request.query_params.get("point")
        user = self.request.query_params.get("user")
        counter = self.request.query_params.get("counter")

        start_date = self.request.query_params.get("start_date")
        end_date = self.request.query_params.get("end_date")


        queryset = Monitoring.objects.all()

        # Debugging: Print the incoming values
        print(f"Filtering with - Filial: {filial}, Point: {point}, User: {user}")

        filters = Q()

        if start_date and end_date:
            filters &= Q(craeted_at__gte=start_date , created_at__lte=end_date)

        if counter:
            filters &= Q(counter = counter)
        if user:
            filters &= Q(user_id=user)  # Ensure this matches your model field
        if point:
            filters &= Q(point_id=point)  # Ensure this matches your model field
        if filial:
            filters &= Q(point__filial_id=filial)  # If Filial is linked via Point

        if asos:
            filters &= Q(point__asos__id=asos)

        if creator:
            filters &= Q(point__creator__id=creator)

        queryset = queryset.filter(filters)

        # Debugging: Print query results
        print(f"Filtered Queryset Count: {queryset.count()}")

        return queryset


class MonitoringRetrieveView(RetrieveUpdateDestroyAPIView):
    queryset = Monitoring.objects.all()
    serializer_class = MonitoringSerializer
    permission_classes = [IsAuthenticated]


class MonitoringBulkCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # Get the last counter value
        last_counter = Monitoring.objects.order_by('-counter').values_list('counter', flat=True).first() or 0
        counter = last_counter + 1


        if isinstance(request.data, str):
            try:
                data = json.loads(request.data)
            except json.JSONDecodeError:
                return Response({"error": "Invalid JSON format"}, status=400)
        elif isinstance(request.data, dict):
            data = [request.data]
        else:
            data = request.data


        for item in data:
            if isinstance(item, dict):
                item['counter'] = counter
            else:
                return Response({"error": "Each item must be a JSON object"}, status=400)

        serializer = MonitoringSerializer(data=data, many=True, context={'request': request})
        serializer.is_valid(raise_exception=True)
        instances = serializer.save()

        return Response(MonitoringSerializer(instances, many=True).data, status=201)



class Asos4ListCreateView(ListCreateAPIView):
    queryset = ResultSubjects.objects.all()
    serializer_class = ResultPointsSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        asos = self.request.query_params.get("asos")
        name = self.request.query_params.get("name")
        queryset = ResultSubjects.objects.all()
        if name:
            queryset = queryset.filter(result__id=name)
        if asos:
            queryset = queryset.filter(asos__id=asos)

        return queryset


    def get_paginated_response(self, data):
        return Response(data)



class ResultSubjectRetrieveView(RetrieveUpdateDestroyAPIView):
    queryset = ResultSubjects.objects.all()
    serializer_class = ResultPointsSerializer
    permission_classes = [IsAuthenticated]


class StudentCountMonitoringListCreateView(ListCreateAPIView):
    queryset = StudentCountMonitoring.objects.all()
    serializer_class = StudentCountMonitoringSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        asos = self.request.query_params.get("asos")
        filial = self.request.query_params.get("filial")
        if asos:
             return StudentCountMonitoring.objects.filter(asos__id=asos)
        return StudentCountMonitoring.objects.all()

    def get_paginated_response(self, data):
        return Response(data)


class StudentCountRetrieveView(RetrieveUpdateDestroyAPIView):
    queryset = StudentCountMonitoring.objects.all()
    serializer_class = StudentCountMonitoringSerializer
    permission_classes = [IsAuthenticated]



class ResultsNameListCreateView(ListCreateAPIView):
    queryset = ResultName.objects.all()
    serializer_class = ResultsNameSerializer
    permission_classes = [IsAuthenticated]

    def get_paginated_response(self, data):
        return Response(data)


class MonitoringAsosListCreateView(ListAPIView):
    queryset = MonitoringAsos4.objects.all()
    serializer_class = MonitoringAsos4Serializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        asos = self.request.query_params.get("asos")
        user = self.request.query_params.get("user")
        results = self.request.query_params.get("result")
        subject = self.request.query_params.get("subject")

        start_date = self.request.query_params.get("start_date")
        end_date = self.request.query_params.get("end_date")


        queryset = MonitoringAsos4.objects.all()

        if start_date and end_date:
            queryset = queryset.filter(created_at__gte=start_date, created_at__lte=end_date)

        if asos:
            queryset = queryset.filter(asos__id=asos)
        if user:
            queryset = queryset.filter(user_id=user)
        if results:
            queryset = queryset.filter(result__id=results)
        if subject:
            queryset = queryset.filter(subject__id=subject)
        return queryset


    def get_paginated_response(self, data):
        return Response(data)


class CommentsListCreateView(ListCreateAPIView):
    queryset = Comments.objects.all()
    serializer_class = CommentsSerializer
    permission_classes = [IsAuthenticated]


    def get_queryset(self):
        counter = self.request.query_params.get("counter")
        queryset = Comments.objects.all()
        if counter:
            queryset = queryset.filter(monitoring__counter=counter)
        return queryset

    def get_paginated_response(self, data):
        return Response(data)


class Monitoring5List(ListAPIView):
    queryset = Monitoring5.objects.all()
    serializer_class = Monitoring5Serializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):

        start_date = self.request.query_params.get("start_date")
        end_date = self.request.query_params.get("end_date")
        teacher = self.request.query_params.get("teacher")

        queryset = Monitoring5.objects.all()

        if start_date and end_date:
            queryset = Monitoring5.objects.all(created_at__gte=start_date, created_at__lte=end_date)

        if teacher:
            queryset = queryset.filter(teacher__id=teacher)
        return queryset