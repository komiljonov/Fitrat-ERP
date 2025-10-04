# yourapp/checks.py
import sys
from django.core.checks import register, Error, Tags
from django.apps import apps
from django.db import connections

from django.core import checks

from data.command.models import BaseModel


@register()
def ensure_archive_constraint(app_configs, **kwargs):
    errors = []
    for model in apps.get_models():
        if not issubclass(model, BaseModel) or model._meta.abstract:
            continue

        # print([[str(c.condition), str(c.condition)] for c in model._meta.constraints])

        # look for our constraint condition signature
        cond_ok = any(
            getattr(c, "condition", None) is not None
            and "is_archived" in str(c.condition)
            and "archived_at__isnull" in str(c.condition)
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


REQUIRED_EXTENSIONS = {"btree_gist", "btree_gin"}  # add more if you need


@register(Tags.database)
def check_postgres_extensions(app_configs, **kwargs):

    if "psql_ext" in sys.argv:
        return []

    errors = []
    for alias in connections:
        conn = connections[alias]
        # Only enforce on PostgreSQL backends
        if "postgresql" not in conn.vendor:
            continue
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT extname FROM pg_extension;")
                installed = {row[0] for row in cur.fetchall()}
        except Exception as e:
            errors.append(
                checks.Error(
                    f"[{alias}] Could not query pg_extension: {e}",
                    id="PG.E000",
                )
            )
            continue

        missing = REQUIRED_EXTENSIONS - installed
        if missing:
            errors.append(
                checks.Error(
                    f"[{alias}] Missing PostgreSQL extensions: {', '.join(sorted(missing))}",
                    hint="Run: python manage.py enable_pg_extensions",
                    id="PG.E001",
                )
            )
    return errors
