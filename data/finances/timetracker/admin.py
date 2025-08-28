from django.contrib import admin

from .models import Employee_attendance, UserTimeLine, Stuff_Attendance


# Register your models here.


@admin.register(Employee_attendance)
class FinansAdmin(admin.ModelAdmin):
    list_display = ('employee__full_name', "amount","status","date")
    search_fields = ('employee__full_name', "amount","status")
    list_filter = ('employee__full_name', "amount","status")


@admin.register(Stuff_Attendance)
class StuffAttendanceAdmin(admin.ModelAdmin):
    list_display = ('employee__full_name','check_in',"check_out","not_marked","date", "amount","action")


@admin.register(UserTimeLine)
class UserTimeLineAdmin(admin.ModelAdmin):
    list_display = ('user__full_name', 'day',"start_time", "end_time")
    search_fields = ('user__full_name', 'day', 'start_time', 'end_time')
    list_filter = ('user__full_name', 'day', 'start_time', 'end_time')