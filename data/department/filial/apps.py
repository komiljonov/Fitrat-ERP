from django.apps import AppConfig


class FilialConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'data.department.filial'

    def ready(self):
        import data.department.filial.signals