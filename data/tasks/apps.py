from django.apps import AppConfig


class TasksConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'data.tasks'

    def ready(self):
        import data.tasks.signals