from uuid import UUID

from data.student.student.v2.serializers import StudentFreezeSerializer
from django.shortcuts import get_object_or_404
from django.utils import timezone

from django.db.models import Sum

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import HttpRequest, Request
from rest_framework.exceptions import ValidationError

from data.archive.models import Archive
from data.student.student.models import Student
from data.student.student.v2.filters import StudentFilter


# views.py
class StudentsStatsAPIView(APIView):
    STAGE_MAP = {"new": "NEW_STUDENT", "active": "ACTIVE_STUDENT", "all": "ALL"}

    def get(self, request: HttpRequest, stage: str):

        stage_type = self.STAGE_MAP.get(stage)

        if not stage_type:
            return Response({"error": "Invalid stage"}, status=400)

        if stage_type != "ALL":

            students = Student.objects.filter(
                is_archived=False,
                student_stage_type=stage_type,
            )
        else:
            students = Student.objects.filter(is_archived=False)

        s_f = StudentFilter(
            data=request.query_params, queryset=students, request=request
        )
        students = s_f.qs

        entitled = students.filter(balance__gte=100000)
        near_debt = students.filter(balance__gt=0, balance__lt=100000)
        indebted = students.filter(balance__lt=0)

        ever_archived = Archive.objects.filter(
            student__student_stage_type=stage_type,
        )

        return Response(
            {
                "total": students.count(),
                "entitled": {
                    "count": entitled.count(),
                    "amount": entitled.aggregate(total=Sum("balance"))["total"] or 0,
                    # "ids": entitled.values_list("id", "first_name", "balance"),
                },
                "indebted": {
                    "count": indebted.count(),
                    "amount": indebted.aggregate(total=Sum("balance"))["total"] or 0,
                    # "ids": indebted.values_list("id", "first_name", "balance"),
                },
                "near_debt": {
                    "count": near_debt.count(),
                    "amount": near_debt.aggregate(total=Sum("balance"))["total"] or 0,
                    # "ids": near_debt.values_list("id", "first_name", "balance"),
                },
                "archived": ever_archived.count(),
            }
        )


class StudentFreezeAPIView(APIView):

    def post(self, request: HttpRequest | Request, pk: UUID):
        serializer = StudentFreezeSerializer(data=request.data)
        if not serializer.is_valid():
            raise ValidationError(serializer.errors)

        student = get_object_or_404(Student, pk=pk)
        today = timezone.now().date()
        print(serializer.data.get("frozen_reason"))
        student.frozen_from_date = today
        student.frozen_till_date = serializer.data.get("frozen_till_date")
        student.frozen_reason = serializer.data.get("frozen_reason")

        student.save()

        return Response(data={
            "message": "ok"
        }, status=200)
        