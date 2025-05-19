from django.apps import AppConfig


class CompensationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'data.finances.compensation'

    # def ready(self):
    #     import data.finances.compensation.signals