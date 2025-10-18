from django.apps import AppConfig


class TransactionsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'data.student.transactions'

    def ready(self):
        import data.student.transactions.signals