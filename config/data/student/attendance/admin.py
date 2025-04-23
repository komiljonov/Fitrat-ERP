from django.contrib import admin

from .models import Attendance, SecondaryAttendance
from ..student.models import Student


# Register your models here.
@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ( 'lid','student',"group",'reason')
    list_filter = ('reason',)
    search_fields = ('reason',)


@admin.register(SecondaryAttendance)
class SecondaryAttendanceAdmin(admin.ModelAdmin):
    list_display = ('student',"group",'reason',"created_at")
    list_filter = ('reason',"student__first_name",'student__last_name',"student__phone")
    search_fields = ('reason',"student__first_name",'student__last_name',"student__phone")

