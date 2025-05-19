from django.apps import AppConfig


class FinansConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'data.finances.finance'

    # def ready(self):
    #      import data.finances.finance.signals
