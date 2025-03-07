from django.contrib import admin

from .models import Attendance


# Register your models here.
@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ( 'lid','student',"group",'reason')
    list_filter = ('reason',)
    search_fields = ('reason',)