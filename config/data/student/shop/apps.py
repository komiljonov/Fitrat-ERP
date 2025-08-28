from django.apps import AppConfig


class ShopConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'data.student.shop'

    def ready(self):
        import data.student.shop.signals