# views.py

import json
from django.http import HttpResponse
from rest_framework.views import APIView
from .models import Theme
from .serializers import ThemeDumpSerializer
import uuid

class ThemeDumpDownloadAPIView(APIView):
    def get(self, request):
        themes = Theme.objects.all()
        serializer = ThemeDumpSerializer(themes, many=True)

        dump = [
            {
                "model": "subject.theme",
                "pk": str(obj["id"]) if obj.get("id") else str(uuid.uuid4()),
                "fields": {k: v for k, v in obj.items() if k != "id"},
            }
            for obj in serializer.data
        ]

        # Convert to JSON string
        dump_json = json.dumps(dump, indent=2, ensure_ascii=False)

        # Return as downloadable JSON file
        response = HttpResponse(dump_json, content_type='application/json')
        response['Content-Disposition'] = 'attachment; filename="theme_dump.json"'
        return response
