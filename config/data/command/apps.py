from django.apps import AppConfig


class CommandConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "data.command"

    def ready(self):
        import data.command.check
        import data.command.lookup
