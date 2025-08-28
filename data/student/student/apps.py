from django.apps import AppConfig


class StudentConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'data.student.student'

    def ready(self):
        import data.student.student.signals