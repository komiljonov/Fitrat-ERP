from django.apps import AppConfig


class EmployeeConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "data.employee"

    def ready(self):
        import data.employee.signals
