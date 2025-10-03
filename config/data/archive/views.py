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

        archives = Archive.objects.filter(unarchived_at=None)

        archived_leads = archives.filter(lead__lid_stage_type="NEW_LID")
        archived_orders = archives.filter(lead__lid_stage_type="ORDERED_LID")

        archived_new_students = archives.filter(student_stage_type="NEW_STUDENT")
        archived_active_students = archives.filter(student_stage_type="ACTIVE_STUDENT")

        return Response(
            {
                "total": archives.count(),
                "leads": archived_leads.count(),
                "orders": archived_orders.count(),
                "new_students": archived_new_students.count(),
                "active_students": archived_active_students.count(),
            }
        )
