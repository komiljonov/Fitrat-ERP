from django.http import HttpRequest

from django.db.models import Sum

from rest_framework.views import APIView
from rest_framework.response import Response

from data.archive.models import Archive
from data.student.student.models import Student
from data.student.student.v2.filters import StudentFilter


class NewStudentsStatsAPIView(APIView):

    def get(self, request: HttpRequest):

        students = Student.objects.filter(
            is_archived=False,
            student_stage_type="NEW_STUDENT",
        )

        s_f = StudentFilter(
            data=request.query_params, queryset=students, request=request
        )

        students = s_f.qs

        entitled = students.filter(balance__gt=0)
        indebted = students.filter(balance__lt=0)

        ever_archived = Archive.objects.filter(
            student__student_stage_type="NEW_STUDENT",
        )

        return Response(
            {
                "total": students.count(),
                "entitled": {
                    "count": entitled.count(),
                    "amount": entitled.aggregate(total=Sum("balance")),
                    "ids": entitled.values_list("id", "first_name", "balance"),
                },
                "indebted": {
                    "count": indebted.count(),
                    "amount": indebted.aggregate(total=Sum("balance")),
                    "ids": indebted.values_list("id", "first_name", "balance"),
                },
                "archived": ever_archived.count(),
                "activated": Student.objects.filter(
                    student_stage_type="ACTIVE_STUDENT"
                ).count(),
            }
        )
