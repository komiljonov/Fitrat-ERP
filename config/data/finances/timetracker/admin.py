from django.contrib import admin

from .models import Employee_attendance, UserTimeLine


# Register your models here.


@admin.register(Employee_attendance)
class FinansAdmin(admin.ModelAdmin):
    list_display = ('employee__full_name', "check_in","check_out")
    search_fields = ('employee__full_name', "check_in","check_out")
    list_filter = ('employee__full_name', "check_in","check_out")


@admin.register(UserTimeLine)
class UserTimeLineAdmin(admin.ModelAdmin):
    list_display = ('user__full_name', 'day',"start_time", "end_time")
    search_fields = ('user__full_name', 'day', 'start_time', 'end_time')
    list_filter = ('user__full_name', 'day', 'start_time', 'end_time')