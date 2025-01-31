from django.apps import AppConfig


class StudentgroupConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'data.student.studentgroup'

    # def ready(self):
    #     import data.student.studentgroup.