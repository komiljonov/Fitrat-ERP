python manage.py dumpdata \
  --exclude=timetracker.Stuff_Attendance \
  --exclude=logs.Log \
  --exclude=notifications.Notification \
  --exclude=contenttypes \
  --exclude=auth.Permission \
  --exclude=admin.LogEntry \
  --exclude=sessions \
  > backup.json