# views.py

import json
from django.http import HttpResponse
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Theme
from data.student.subject.serializers import (
    ThemeDumpSerializer,
)
import uuid


class ThemeDumpDownloadAPIView(APIView):
    def get(self, request):

        course = self.request.GET.get("course")

        themes = Theme.objects.all()

        if course:
            themes = themes.filter(course__id=course)
        serializer = ThemeDumpSerializer(themes, many=True)

        dump = [
            {
                "model": "subject.theme",
                "pk": str(obj["id"]) if obj.get("id") else str(uuid.uuid4()),
                "fields": {k: v for k, v in obj.items() if k != "id"},
            }
            for obj in serializer.data
        ]

        # Fix: Convert all unknown types (like UUID) using `default=str`
        dump_json = json.dumps(dump, indent=2, ensure_ascii=False, default=str)

        response = HttpResponse(dump_json, content_type="application/json")
        response["Content-Disposition"] = 'attachment; filename="theme_dump.json"'
        return response


class ThemeBulkCreateAPIView(APIView):
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_ARRAY,
            items=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "model": openapi.Schema(type=openapi.TYPE_STRING),
                    "pk": openapi.Schema(type=openapi.TYPE_STRING, format="uuid"),
                    "fields": openapi.Schema(type=openapi.TYPE_OBJECT),
                },
                required=["model", "pk", "fields"],
            ),
        ),
        responses={
            201: openapi.Response(
                "Themes created successfully", ThemeDumpSerializer(many=True)
            ),
            400: openapi.Response("Invalid data or format"),
        },
        operation_summary="Bulk create themes (fixture-compatible)",
        operation_description="Accepts a list of theme objects in Django fixture format and creates them in bulk.",
    )
    def post(self, request):
        data = request.data

        if not isinstance(data, list):
            return Response(
                {"error": "Expected a list of theme objects."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Convert Django fixture format to serializer-compatible format
        transformed_data = []
        for obj in data:
            if not isinstance(obj, dict) or "fields" not in obj:
                return Response(
                    {"error": "Each item must contain 'fields'"}, status=400
                )
            theme_data = obj["fields"]
            if "pk" in obj or "id" in obj:
                theme_data["id"] = obj.get("pk") or obj.get("id")
            transformed_data.append(theme_data)

        serializer = ThemeDumpSerializer(data=transformed_data, many=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(
            {"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
        )
