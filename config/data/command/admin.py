from django.contrib import admin, messages

from django.apps import apps
from django.db import transaction


print("Registering models")


def _merge_actions(existing, extra):
    """Return a list with existing actions first, then any extras not already present."""
    out = list(existing or [])
    for a in extra:
        if a not in out:
            out.append(a)
    return out


class ResaveActionMixin:
    @admin.action(description="Re-save selected items (trigger signals)")
    def resave_objects(self, request, queryset):
        total, errors = 0, 0
        for obj in queryset.iterator(chunk_size=200):
            try:
                with transaction.atomic():
                    obj.save()
                total += 1
            except Exception:
                errors += 1
        msg = f"Re-saved {total} object(s)."
        if errors:
            msg += f" {errors} failed—check logs."
        self.message_user(request, msg, level=messages.INFO)


models = apps.get_models()

for model in models:
    try:
        if hasattr(model, "Admin"):
            modelAdmin = getattr(model, "Admin")

            # Dynamically build a subclass that mixes in the action and merges `actions`
            @admin.register(model)
            class ModelAdmin(ResaveActionMixin, modelAdmin):  # type: ignore[misc]
                # merge existing actions with our resave action
                actions = _merge_actions(
                    getattr(modelAdmin, "actions", []), ["resave_objects"]
                )
                pass

        else:

            @admin.register(model)
            class ModelAdmin(ResaveActionMixin, admin.ModelAdmin):
                actions = _merge_actions(
                    getattr(admin.ModelAdmin, "actions", []), ["resave_objects"]
                )
                pass

    except admin.sites.AlreadyRegistered:
        pass

print("Registering models ------------------------ END")
