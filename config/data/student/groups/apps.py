from django.apps import AppConfig


class GroupsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'data.student.groups'

    def ready(self):
        import data.student.groups.signals
