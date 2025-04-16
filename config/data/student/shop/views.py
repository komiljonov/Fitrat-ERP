from decimal import Decimal

from rest_framework import status
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Coins, Points, Products, Purchase, Category
from .serializers import CoinsSerializer, PointsSerializer, ProductsSerializer, PurchaseSerializer, \
    PointToCoinExchangeSerializer, CategoriesSerializer
from ..student.models import Student


class CoinsList(ListCreateAPIView):
    queryset = Coins.objects.all()
    serializer_class = CoinsSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Coins.objects.all()
        student = self.request.query_params.get('student')
        is_exchanged = self.request.query_params.get('is_exchanged')

        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')

        if start_date and end_date:
            queryset = queryset.filter(created_at__gte=start_date, created_at__lte=end_date)
        if start_date:
            queryset = queryset.filter(created_at__gte=start_date)
        if student:
            queryset = queryset.filter(student__id=student)
        if is_exchanged:
            queryset = queryset.filter(is_exchanged=is_exchanged.capitalize())
        return queryset


class CoinsDetail(RetrieveUpdateDestroyAPIView):
    queryset = Coins.objects.all()
    serializer_class = CoinsSerializer
    permission_classes = [IsAuthenticated]


class PointsList(ListCreateAPIView):
    queryset = Points.objects.all()
    serializer_class = PointsSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Points.objects.all()
        student = self.request.query_params.get('student')
        is_exchanged = self.request.query_params.get('is_exchanged')
        from_test = self.request.query_params.get('from_test')
        from_homework = self.request.query_params.get('from_homework')

        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')

        if start_date and end_date:
            queryset = queryset.filter(created_at__gte=start_date, created_at__lte=end_date)
        if start_date:
            queryset = queryset.filter(created_at__gte=start_date)

        if student:
            queryset = queryset.filter(student__id=student)
        if is_exchanged:
            queryset = queryset.filter(is_exchanged=is_exchanged.capitalize())
        if from_test:
            queryset = queryset.filter(from_test__id=from_test)
        if from_homework:
            queryset = queryset.filter(from_homework__id=from_homework)

        return queryset


class PointsDetail(RetrieveUpdateDestroyAPIView):
    queryset = Points.objects.all()
    serializer_class = PointsSerializer
    permission_classes = [IsAuthenticated]


class ProductsList(ListCreateAPIView):
    queryset = Products.objects.all()
    serializer_class = ProductsSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        category = self.request.query_params.get('category')
        search = self.request.query_params.get('search')

        queryset = Products.objects.all()

        if search:
            queryset = queryset.filter(name__icontains=search)

        if category:
            queryset = queryset.filter(category__id=category)
        return queryset


class ProductsDetail(RetrieveUpdateDestroyAPIView):
    queryset = Products.objects.all()
    serializer_class = ProductsSerializer
    permission_classes = [IsAuthenticated]


class PurchaseList(ListCreateAPIView):
    queryset = Purchase.objects.all()
    serializer_class = PurchaseSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        queryset = Purchase.objects.all()
        user = self.request.query_params.get('user')
        student = self.request.query_params.get('student')

        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')

        if user:
            queryset = queryset.filter(student__user__id=user)

        if start_date and end_date:
            queryset = queryset.filter(created_at__gte=start_date, created_at__lte=end_date)

        if start_date:
            queryset = queryset.filter(created_at__gte=start_date)

        if student:
            queryset = queryset.filter(student__id=student)

        return queryset
    def get_paginated_response(self, data):
        return Response(data)


class PurchaseDetail(RetrieveUpdateDestroyAPIView):
    queryset = Purchase.objects.all()
    serializer_class = PurchaseSerializer
    permission_classes = [IsAuthenticated]


class PointToCoinExchangeApiView(APIView):

    def post(self, request, *args, **kwargs):
        serializer = PointToCoinExchangeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        point_amount = serializer.validated_data['point']
        student_id = serializer.validated_data['student']

        user = Student.objects.get(id=student_id)
        if not user.points < point_amount:
            return Response({"detail": "Not enough points."}, status=status.HTTP_400_BAD_REQUEST)

        # Calculate coins
        coins_to_add = int(point_amount / Decimal('10'))

        # Deduct points
        user.points -= point_amount
        user.save()

        # Create coin
        Coins.objects.create(student=user, coin=coins_to_add)

        return Response({
            "message": "Exchange successful",
            "coins_received": coins_to_add,
            "remaining_points": user.points
        }, status=status.HTTP_201_CREATED)


class CategoryList(ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategoriesSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Category.objects.all()
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(name__icontains=search)
        return queryset

    def get_paginated_response(self, data):
        return Response(data)


class CategoryDetail(RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategoriesSerializer
    permission_classes = [IsAuthenticated]
