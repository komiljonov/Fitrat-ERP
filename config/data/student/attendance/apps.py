from django.apps import AppConfig


class AttendanceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'data.student.attendance'

    # def ready(self):
    #     import data.student.attendance.signals