from django.apps import AppConfig


class MasteringConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'data.student.mastering'

    # def ready(self):
    #      import data.student.mastering.signals
