from django.shortcuts import get_object_or_404

from rest_framework.generics import ListAPIView
from rest_framework.views import APIView
from rest_framework import status

from rest_framework.response import Response


from data.student.subject.models import Level, Theme
from data.student.subject.serializers import ThemeSerializer
from data.student.subject.v2.filters import ThemeFilter
from django.db import transaction


class ThemeNoPgListAPIView(ListAPIView):

    serializer_class = ThemeSerializer.only("id", "title", "description")
    pagination_class = None

    queryset = Theme.objects.filter(is_archived=False)

    filterset_class = ThemeFilter


class ThemeReorderAPIView(APIView):

    @transaction.atomic
    def patch(self, request, *args, **kwargs):
        data = request.data
        if not isinstance(data, list):
            return Response(
                {"detail": "Expected a list of objects."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        updated = []
        for item in data:
            obj = get_object_or_404(Theme, id=item["id"])
            obj.order = item["order"]
            obj.save(update_fields=["order"])
            updated.append({"id": str(obj.id), "order": obj.order})

        return Response({"updated": updated}, status=status.HTTP_200_OK)


class LevelReOrderAPIView(APIView):

    @transaction.atomic
    def patch(self, request, *args, **kwargs):
        data = request.data
        if not isinstance(data, list):
            return Response(
                {"detail": "Expected a list of objects."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        updated = []
        for item in data:
            obj = get_object_or_404(Level, id=item["id"])
            obj.order = item["order"]
            obj.save(update_fields=["order"])
            updated.append({"id": str(obj.id), "order": obj.order})

        return Response({"updated": updated}, status=status.HTTP_200_OK)
