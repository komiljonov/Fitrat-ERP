from django.apps import AppConfig


class MarketingChannelConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'data.department.marketing_channel'

    def ready(self):
        import data.department.marketing_channel.signals