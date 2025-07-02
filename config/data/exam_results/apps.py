from django.apps import AppConfig


class ExamResultsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'data.exam_results'

    def ready(self):
        import data.exam_results.signals