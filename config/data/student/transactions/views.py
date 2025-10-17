# django

# rest framework
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter

# models
from data.student.transactions.models import StudentTransaction
from rest_framework.filters import SearchFilter
from rest_framework.generics import ListCreateAPIView
from rest_framework.permissions import IsAuthenticated

# serializers
from data.student.transactions.serializers import StudentTransactionSerializer


class TransactionListAPIView(ListCreateAPIView):
    queryset = StudentTransaction.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = StudentTransactionSerializer
    filter_backends = (DjangoFilterBackend, OrderingFilter, SearchFilter)
    filterset_fields = ['student']