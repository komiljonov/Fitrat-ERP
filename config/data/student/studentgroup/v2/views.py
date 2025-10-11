from typing import Dict
from django.db.models import Q

from rest_framework.views import APIView
from rest_framework.request import HttpRequest, Request
from rest_framework.response import Response

from data.student.studentgroup.models import (
    SecondaryStudentGroup,
    StudentGroup,
    StudentGroupPrice,
)
from data.student.studentgroup.v2.serializers import (
    GroupStatisticsFilterSerializer,
    StudentGroupPriceSerializer,
)


from rest_framework.generics import ListCreateAPIView


class GroupStatisticsAPIView(APIView):

    def get(self, request: HttpRequest | Request):

        serializer = GroupStatisticsFilterSerializer(data=request.GET)

        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        active_groups = self.active_groups_stats(data)
        ended_groups = self.ended_groups_stats(data)
        secondary_groups = self.secondary_groups_stats(data)

        return Response(
            {
                "active_groups": active_groups,
                "ended_groups": ended_groups,
                "secondary_groups": secondary_groups,
            }
        )

    def active_groups_stats(self, data: Dict):

        students = StudentGroup.objects.filter(
            Q(student__is_archived=False) | Q(lid__is_archived=False),
            group__status="ACTIVE",
        )

        start_date = data.get("start_date")
        end_date = data.get("end_date")

        if start_date and end_date:
            students = students.filter(created_at__range=(start_date, end_date))

        elif start_date:
            students = students.filter(created_at__gte=start_date)

        elif end_date:
            students = students.filter(created_at__lte=end_date)

        if filial := data.get("filial"):
            students = students.filter(group__filial=filial)

        if course := data.get("course"):

            students = students.filter(group__course=course)

        if teacher := data.get("teacher"):

            students = students.filter(group__teacher=teacher)

        all_students = students.filter(is_archived=False)

        orders = students.filter(
            lid__isnull=False,
            lid__lid_stage_type="ORDERED_LID",
            lid__is_student=False,
            is_archived=False,
        )

        students = students.filter(
            student__isnull=False,
            student__is_frozen=False,
            is_archived=False,
        )

        archived_or_frozen = students.filter(
            student__is_frozen=True,
            is_archived=False,
        )

        return {
            "total": all_students.count(),
            "orders": orders.count(),
            "students": students.count(),
            "frozen": archived_or_frozen.count(),
        }

    def ended_groups_stats(self, data: Dict):

        students = StudentGroup.objects.filter(
            Q(student__is_archived=False) | Q(lid__is_archived=False),
            group__status="INACTIVE",
        )

        start_date = data.get("start_date")
        end_date = data.get("end_date")

        if start_date and end_date:
            students = students.filter(created_at__range=(start_date, end_date))

        elif start_date:
            students = students.filter(created_at__gte=start_date)

        elif end_date:
            students = students.filter(created_at__lte=end_date)

        if filial := data.get("filial"):
            students = students.filter(group__filial=filial)

        if course := data.get("course"):

            students = students.filter(group__course=course)

        if teacher := data.get("teacher"):

            students = students.filter(group__teacher=teacher)

        all_students = students.filter(is_archived=False)

        orders = students.filter(
            lid__isnull=False,
            lid__lid_stage_type="ORDERED_LID",
            lid__is_student=False,
            is_archived=False,
        )

        students = students.filter(
            student__isnull=False,
            student__is_frozen=False,
            is_archived=False,
        )

        archived_or_frozen = students.filter(
            student__is_frozen=True,
            is_archived=False,
        )

        return {
            "total": all_students.count(),
            "orders": orders.count(),
            "students": students.count(),
            "frozen": archived_or_frozen.count(),
        }

    def secondary_groups_stats(self, data: Dict):

        students = SecondaryStudentGroup.objects.filter(
            Q(student__is_archived=False) | Q(lid__is_archived=False),
            group__status="ACTIVE",
        )

        start_date = data.get("start_date")
        end_date = data.get("end_date")

        if start_date and end_date:
            students = students.filter(created_at__range=(start_date, end_date))

        elif start_date:
            students = students.filter(created_at__gte=start_date)

        elif end_date:
            students = students.filter(created_at__lte=end_date)

        if filial := data.get("filial"):
            students = students.filter(group__group__filial=filial)

        if course := data.get("course"):

            students = students.filter(group__group__course=course)

        if teacher := data.get("teacher"):

            students = students.filter(group__teacher=teacher)

        all_students = students.filter(is_archived=False)

        orders = students.filter(
            lid__isnull=False,
            lid__lid_stage_type="ORDERED_LID",
            lid__is_student=False,
            is_archived=False,
        )

        students = students.filter(
            student__isnull=False,
            student__is_frozen=False,
            is_archived=False,
        )

        archived_or_frozen = students.filter(
            student__is_frozen=True,
            is_archived=False,
        )

        return {
            "total": all_students.count(),
            "orders": orders.count(),
            "students": students.count(),
            "frozen": archived_or_frozen.count(),
        }


class StudentGroupPriceCreateAPIView(ListCreateAPIView):

    serializer_class = StudentGroupPriceSerializer

    queryset = StudentGroupPrice.objects.all()

    def get_queryset(self):
        qs = super().get_queryset()
        sg_id = self.request.query_params.get("student_group")
        student_id = self.request.query_params.get("student")

        cond = Q()

        if sg_id:
            cond &= Q(student_group_id=sg_id)
        if student_id:
            cond &= Q(student_group__student_id=student_id)

        if cond:
            qs = qs.filter(cond)

        return qs.select_related("student_group", "student_group__student").distinct()
