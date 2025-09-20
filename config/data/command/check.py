# yourapp/checks.py
from django.core.checks import register, Error
from django.apps import apps

from data.command.models import BaseModel


@register()
def ensure_archive_constraint(app_configs, **kwargs):
    errors = []
    for model in apps.get_models():
        if not issubclass(model, BaseModel) or model._meta.abstract:
            continue

        # look for our constraint condition signature
        cond_ok = any(
            getattr(c, "condition", None) is not None
            and "is_archived" in str(c.condition)
            and "archived_at__isnull=False" in str(c.condition)
            for c in model._meta.constraints
        )
        if not cond_ok:
            errors.append(
                Error(
                    f"{model._meta.label} is missing archive constraint "
                    "(inherits BaseModel but overrides Meta incorrectly).",
                    id="yourapp.E001",
                )
            )
    return errors
