from django.contrib import admin

from .models import Attendance


# Register your models here.
@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('theme', 'lid','student','reason')
    list_filter = ('theme','reason')
    search_fields = ('theme','reason')