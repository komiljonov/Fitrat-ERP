from django.apps import AppConfig


class PaycomuzConfig(AppConfig):
    name = 'data.paycomuz'

    def ready(self):
        import data.paycomuz.signals