from rest_framework.generics import ListCreateAPIView, DestroyAPIView
from rest_framework.permissions import IsAuthenticated

from .models import File, Contract
from .serializers import FileUploadSerializer, ContractUploadSerializer


class UploadFileAPIView(ListCreateAPIView):

    serializer_class = FileUploadSerializer
    permission_classes = [IsAuthenticated]
    queryset = File.objects.all()


class UploadDestroyAPIView(DestroyAPIView):
    serializer_class = FileUploadSerializer
    permission_classes = [IsAuthenticated]
    queryset = File.objects.all()


class ContratListAPIView(ListCreateAPIView):
    serializer_class = ContractUploadSerializer
    permission_classes = [IsAuthenticated]
    queryset = Contract.objects.all()