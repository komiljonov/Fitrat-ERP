from django.utils import timezone
from rest_framework.generics import ListAPIView, RetrieveDestroyAPIView

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

        instance.unarchived_at = timezone.now()
        instance.unarchived_by = (
            self.request.user if self.request.user.is_authenticated else None
        )
        instance.save()
