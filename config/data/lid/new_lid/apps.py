from django.apps import AppConfig




class NewLidConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'data.lid.new_lid'

    # def ready(self):
    #     import data.lid.new_lid.signals
