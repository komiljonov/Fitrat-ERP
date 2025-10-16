from django.http import HttpRequest
from rest_framework.generics import ListAPIView, RetrieveDestroyAPIView
from rest_framework.views import APIView
from rest_framework.response import Response


from django.db import transaction
from django.db.models import Q, Sum, Case, When, F, DecimalField


from data.archive.filters import ArchiveFilter
from data.archive.models import Archive
from data.archive.serializers import ArchiveSerializer

# Create your views here.


class ArchiveListAPIView(ListAPIView):

    queryset = Archive.objects.filter(unarchived_at=None)
    serializer_class = ArchiveSerializer

    filterset_class = ArchiveFilter

    def get_queryset(self):
        queryset = Archive.objects.filter(unarchived_at=None)
        start_date = self.request.GET.get("start_date")
        end_date = self.request.GET.get("end_date")
        if start_date and end_date:
            print(start_date, end_date)
            queryset = queryset.filter(created_at__date__lte=end_date, created_at__date__gte=start_date)
        return super().get_queryset()


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

        f = ArchiveFilter(data=request.query_params, queryset=archives, request=request)

        archives = f.qs

        archived_leads = archives.filter(lead__lid_stage_type="NEW_LID")
        archived_orders = archives.filter(lead__lid_stage_type="ORDERED_LID")

        archived_new_students = archives.filter(
            student__student_stage_type="NEW_STUDENT"
        )
        archived_active_students = archives.filter(
            student__student_stage_type="ACTIVE_STUDENT"
        )

        entitled = archives.filter(Q(lead__balance__gt=0) | Q(student__balance__gt=0))
        indebted = archives.filter(Q(lead__balance__lt=0) | Q(student__balance__lt=0))

        # use conditional CASE so we can handle both lead and student balances in one total
        entitled_total = (
            entitled.aggregate(
                total=Sum(
                    Case(
                        When(lead__isnull=False, then=F("lead__balance")),
                        When(student__isnull=False, then=F("student__balance")),
                        output_field=DecimalField(),
                    )
                )
            )["total"]
            or 0
        )

        indebted_total = (
            indebted.aggregate(
                total=Sum(
                    Case(
                        When(lead__isnull=False, then=F("lead__balance")),
                        When(student__isnull=False, then=F("student__balance")),
                        output_field=DecimalField(),
                    )
                )
            )["total"]
            or 0
        )

        return Response(
            {
                "total": archives.count(),
                "leads": archived_leads.count(),
                "orders": archived_orders.count(),
                "new_students": archived_new_students.count(),
                "active_students": archived_active_students.count(),
                "entitled": {
                    "count": entitled.count(),
                    "total_amount": entitled_total,
                    # "ids": entitled.values_list("id", flat=True),
                },
                "indebted": {
                    "count": indebted.count(),
                    "total_amount": indebted_total,
                    # "ids": indebted.values_list("id", flat=True),
                },
            }
        )
