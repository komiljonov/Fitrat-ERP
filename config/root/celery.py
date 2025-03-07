import os
from celery.schedules import crontab


from celery import Celery


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "root.settings")

app = Celery("root")


app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()


app.conf.beat_schedule = {
    'send-daily-messages': {
        'task': 'data.tasks.tasks.check_daily_tasks',
        'schedule': crontab(minute='*/1'),
    },
    'check-daily-leads': {
            'task': 'data.lid.new_lid.tasks.check_daily_leads',
            'schedule': crontab(minute='*/1'),
        },
    "check_attendance_daily": {
            "task": "app.tasks.check_daily_user_attendance",
            "schedule": crontab(hour=0, minute=0),
        },

}

app.conf.timezone = "Asia/Tashkent"