from django.shortcuts import get_object_or_404
from drf_yasg.utils import APIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response

from data.student.groups.models import Group
from data.student.subject.models import Level
from data.student.groups.v2.serializers import GroupSerializer
from django.db.models import Count
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework import status


class GroupListAPIView(ListAPIView):

    queryset = Group.objects.select_related("start_theme", "teacher", "filial", "course", "course_subject")

    permission_classes = [IsAuthenticated]
    serializer_class = GroupSerializer
    filter_backends = (DjangoFilterBackend, OrderingFilter, SearchFilter)

    search_fields = (
        "name",
        "status",
        "teacher__id",
        "course__subject__id",
    )

    ordering_fields = (
        "name",
        "scheduled_day_type",
        "start_date",
        "end_date",
        # "price_type",
        "status",
        "teacher__id",
        "course__subject__id",
    )

    filterset_fields = (
        "name",
        "scheduled_day_type__name",
        # "price_type",
        "status",
        "teacher__id",
        "course__subject__id",
    )

    def get_queryset(self):
        queryset = Group.objects.all()
        teacher = self.request.GET.get("teacher", None)
        course = self.request.GET.get("course", None)
        subject = self.request.GET.get("subject", None)
        filial = self.request.GET.get("filial", None)

        if teacher:
            queryset = queryset.filter(teacher_id=teacher)

        if course:
            queryset = queryset.filter(course_id=course)

        if subject:
            queryset = queryset.filter(course__subject_id=subject)

        if filial and filial.isnumeric():
            queryset = queryset.filter(filial_id=filial)

        queryset = queryset.annotate(student_count=Count("students"))
        return queryset.order_by("-student_count")


class GroupChangeLevelAPIView(APIView):
    def post(self, request, *args, **kwargs):
        pk = kwargs['pk']
        group = get_object_or_404(Group, id=pk)
        current_level = group.level

        levels_qs = (
            Level.objects.filter(courses=group.course, is_archived=False)
            .order_by("order")
        )

        next_level = None
        if current_level is None:
            next_level = levels_qs.first()
        else:
            next_level = levels_qs.filter(order__gt=current_level.order).first()

        if next_level is None:
            group.status = "INACTIVE"
            group.save(update_fields=["status"])
        else:
            group.level = next_level
            group.save(update_fields=["level"])

        return Response({"message": "Created"}, status=status.HTTP_201_CREATED)