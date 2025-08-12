from decimal import Decimal

from rest_framework import status
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Coins, Points, Products, Purchase, Category, CoinsSettings
from .serializers import CoinsSerializer, PointsSerializer, ProductsSerializer, PurchaseSerializer, \
    PointToCoinExchangeSerializer, CategoriesSerializer, CoinsSettingsSerializer
from ..student.models import Student


class CoinsSettingsCreateAPIView(ListCreateAPIView):
    queryset = CoinsSettings.objects.all()
    serializer_class = CoinsSettingsSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = CoinsSettings.objects.all()

        type = self.request.GET.get('type')
        choice = self.request.GET.get('choice')
        if choice:
            queryset = queryset.filter(choice=choice)
        if type:
            queryset = queryset.filter(type=type)
        return queryset


class CoinsSettingsRetrieveAPIView(RetrieveUpdateDestroyAPIView):
    queryset = CoinsSettings.objects.all()
    serializer_class = CoinsSettingsSerializer
    permission_classes = [IsAuthenticated]


class CoinsList(ListCreateAPIView):
    queryset = Coins.objects.all()
    serializer_class = CoinsSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Coins.objects.all()
        student = self.request.GET.get('student')
        status = self.request.GET.get('status')

        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')

        if status:
            queryset = queryset.filter(status=status)

        if start_date and end_date:
            queryset = queryset.filter(created_at__gte=start_date, created_at__lte=end_date)
        if start_date:
            queryset = queryset.filter(created_at__gte=start_date)
        if student:
            queryset = queryset.filter(student__user__id=student)
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
        student = self.request.GET.get('student')
        is_exchanged = self.request.GET.get('is_exchanged')
        from_test = self.request.GET.get('from_test')
        from_homework = self.request.GET.get('from_homework')

        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')

        if start_date and end_date:
            queryset = queryset.filter(created_at__gte=start_date, created_at__lte=end_date)
        if start_date:
            queryset = queryset.filter(created_at__gte=start_date)

        if student:
            queryset = queryset.filter(student__user__id=student)
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
        category = self.request.GET.get('category')
        search = self.request.GET.get('search')
        filial = self.request.GET.get('filial')

        queryset = Products.objects.all()

        if filial:
            queryset = queryset.filter(filial__id=filial)

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
        user = self.request.GET.get('user')
        student = self.request.GET.get('student')

        status = self.request.GET.get('status')
        filial = self.request.GET.get('filial')

        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')

        if filial:
            queryset = queryset.filter(filial__id=filial)

        if status:
            queryset = queryset.filter(status=status)

        if user:
            queryset = queryset.filter(student__user__id=user)

        if start_date and end_date:
            queryset = queryset.filter(created_at__gte=start_date, created_at__lte=end_date)

        if start_date:
            queryset = queryset.filter(created_at__gte=start_date)

        if student:
            queryset = queryset.filter(student__id=student)

        return queryset


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

        user = Student.objects.get(user__id=student_id)
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
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(name__icontains=search)
        return queryset

    def get_paginated_response(self, data):
        return Response(data)


class CategoryDetail(RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategoriesSerializer
    permission_classes = [IsAuthenticated]


class OrdersStatisList(APIView):
    def get(self, request, *args, **kwargs):
        queryset = Purchase.objects.all()

        product = self.request.GET.get('product')
        student = self.request.GET.get('student')
        status = self.request.GET.get('status')
        updater = self.request.GET.get('updater')
        filial = self.request.GET.get('filial')

        filters = {}

        if filial:
            filters['filial__id'] = filial

        # if status:
        #     queryset = queryset.filter(status=status)
        # if student:
        #     queryset = queryset.filter(student__user__id=student)
        # if product:
        #     queryset = queryset.filter(product__id=product)
        # if updater:
        #     queryset = queryset.filter(updater__id=updater)

        complated_orders = Purchase.objects.filter(status="Completed",**filters)
        pending_orders = Purchase.objects.filter(status="Pending",**filters)
        cancalled_orders = Purchase.objects.filter(status="Cancelled",**filters)

        return Response({
            "complated_orders": complated_orders.count(),
            "pending_orders": pending_orders.count(),
            "cancalled_orders": cancalled_orders.count(),
        })
