from rest_framework.generics import ListCreateAPIView, RetrieveDestroyAPIView

from config.data.employee.models import EmployeeTransaction
from config.data.employee.serializers import EmployeeTransactionSerializer


class EmployeeTransactionsListCreateAPIView(ListCreateAPIView):
    """
    GET  /transactions      -> list transactions for all employees
    POST /transactions      -> create a transaction for all employees
    """

    queryset = EmployeeTransaction.objects.all()

    serializer_class = EmployeeTransactionSerializer

    # If your model has timestamps, prefer ordering by -created_at; otherwise -id
    default_ordering = "-created_at"


class EmployeeTransactionRetrieveDestroyAPIView(RetrieveDestroyAPIView):

    queryset = EmployeeTransaction.objects.all()

    serializer_class = EmployeeTransactionSerializer
