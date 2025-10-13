# views.py
from uuid import UUID
from typing import Any, Optional

from django.apps import apps
from django.db import models
from django.forms.models import model_to_dict
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from data.command.models import BaseModel  # adjust path


def _coerce_value(raw: str, pk_field: models.Field) -> Optional[Any]:
    """Coerce id to appropriate type for pk field."""
    try:
        if isinstance(pk_field, models.UUIDField):
            return UUID(raw)
        if isinstance(
            pk_field, (models.IntegerField, models.BigIntegerField, models.AutoField)
        ):
            return int(raw)
        return pk_field.to_python(raw)
    except Exception:
        return None


class FindByIdAcrossModelsAPIView(APIView):
    permission_classes = [IsAuthenticated]  # or []

    def get(self, request):
        raw_id = request.GET.get("id")
        if not raw_id:
            return JsonResponse({"detail": "Provide ?id="}, status=400)

        only_apps = request.GET.get("apps")
        only_apps = {a.strip() for a in only_apps.split(",")} if only_apps else None

        results = []
        for model in apps.get_models():
            if (
                not issubclass(model, BaseModel)
                or model._meta.abstract
                or model._meta.proxy
            ):
                continue
            if only_apps and model._meta.app_label not in only_apps:
                continue

            pk_field = model._meta.pk
            value = _coerce_value(raw_id, pk_field)
            if value is None:
                continue

            try:
                objs = model._default_manager.filter(**{pk_field.name: value})
                for obj in objs:
                    data = model_to_dict(obj)
                    results.append(
                        {
                            "app": model._meta.app_label,
                            "model": model._meta.model_name,
                            "data": data,
                        }
                    )
            except Exception:
                continue

        return JsonResponse(
            {
                "id": raw_id,
                "count": len(results),
                "results": results,
            },
            json_dumps_params={"ensure_ascii": False, "indent": 2},
        )
