from django.contrib import admin

from django.contrib import admin
from django.apps import apps

print("Registering models")
models = apps.get_models()

for model in models:
    try:
        if hasattr(model, "Admin"):
            modelAdmin = getattr(model, "Admin")

            @admin.register(model)
            class ModelAdmin(modelAdmin):  # type: ignore
                model = model
                list_filter = modelAdmin.list_filter

        else:

            @admin.register(model)
            class ModelAdmin(admin.ModelAdmin):
                model = model

    except admin.sites.AlreadyRegistered as e:
        pass
        # print(e)

print("Registering models ------------------------ END")
