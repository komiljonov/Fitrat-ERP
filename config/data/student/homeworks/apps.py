from django.apps import AppConfig


class HomeworksConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'data.student.homeworks'

    # def ready(self):
    #     import data.student.homeworks.signals