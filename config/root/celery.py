import os
from celery.schedules import crontab
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "root.settings")

app = Celery("root")

# ✅ Discover tasks from ALL installed Django apps
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()  # ✅ This ensures all apps are included

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
        "task": "data.finances.timetracker.tasks.check_daily_user_attendance",
        "schedule": crontab(hour=0, minute=0),
    },
    'check-monthly-extra-lessons': {
        'task': 'data.student.mastering.tasks.check_monthly_extra_lessons',
        'schedule': crontab(day_of_month=1, hour=0, minute=0),
    },
    'send_daily_excel_report': {
        'task': "data.dashboard.tasks.send_daily_excel_report",
        'schedule': crontab(hour=9, minute=0),
    },
    "check_accountant_kpi": {
        "task": "data.student.mastering.tasks.check_accountant_kpi",
        "schedule": crontab(hour=20, minute=55),
    }
}

app.conf.timezone = "Asia/Tashkent"
