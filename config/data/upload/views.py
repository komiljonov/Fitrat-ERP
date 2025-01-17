from django.shortcuts import render

from rest_framework.generics import CreateAPIView, ListCreateAPIView

from .models import File
from .serializers import FileUploadSerializer

# Create your views here.


class UploadFileAPIView(ListCreateAPIView):

    serializer_class = FileUploadSerializer
    queryset = File.objects.all()
