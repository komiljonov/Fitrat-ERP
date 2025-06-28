from django.apps import AppConfig


class NotificationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'data.notifications'

    def ready(self):
        import data.notifications.signals
