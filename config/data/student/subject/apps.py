from django.apps import AppConfig


class SubjectConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'data.student.subject'

    def ready(self):
        import data.student.subject.signals