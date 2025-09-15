from django.apps import AppConfig


class FirstlessonConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "data.firstlesson"

    def ready(self):
        import data.firstlesson.signals
