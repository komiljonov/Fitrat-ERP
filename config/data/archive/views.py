from django.http import HttpRequest
from rest_framework.generics import ListAPIView, RetrieveDestroyAPIView
from rest_framework.views import APIView
from rest_framework.response import Response

from django.db import transaction

from data.archive.models import Archive
from data.archive.serializers import ArchiveSerializer

# Create your views here.


class ArchiveListAPIView(ListAPIView):

    queryset = Archive.objects.filter(unarchived_at=None)
    serializer_class = ArchiveSerializer


class ArchiveRetrieveDestroyAPIView(RetrieveDestroyAPIView):

    queryset = Archive.objects.filter(unarchived_at=None)

    serializer_class = ArchiveSerializer

    def perform_destroy(self, instance: Archive):

        with transaction.atomic():

            instance.unarchive()

        instance.save()


class ArchiveStatsAPIView(APIView):

    def get(self, request: HttpRequest):

        return Response({"total": Archive.objects.filter(unarchived_at=None).count()})
