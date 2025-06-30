# views.py

import json
from django.http import HttpResponse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Theme
from .serializers import ThemeDumpSerializer
import uuid

class ThemeDumpDownloadAPIView(APIView):
    def get(self, request):

        course = self.request.GET.get('course')

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

        response = HttpResponse(dump_json, content_type='application/json')
        response['Content-Disposition'] = 'attachment; filename="theme_dump.json"'
        return response


class ThemeBulkCreateAPIView(APIView):
    def post(self, request):
        if not isinstance(request.data, list):
            return Response({"error": "Expected a list of themes"}, status=400)

        serializer = ThemeDumpSerializer(data=request.data, many=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)