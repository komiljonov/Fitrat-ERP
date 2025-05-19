from django.apps import AppConfig


class LessonConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'data.student.lesson'

    def ready(self):
        import data.student.lesson.signals