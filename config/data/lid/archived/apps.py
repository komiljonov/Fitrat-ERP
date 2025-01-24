from django.apps import AppConfig



class ArchivedConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'data.lid.archived'


    def ready(self):
        import data.lid.archived.signals

