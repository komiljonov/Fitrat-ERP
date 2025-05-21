from django.contrib import admin

from .models import Employee_attendance, UserTimeLine


# Register your models here.

#
# @admin.register(Employee_attendance)
# class FinansAdmin(admin.ModelAdmin):
#     list_display = ('user__full_name', 'action')
#     search_fields = ('user__full_name', 'action')
#     list_filter = ('user__full_name', 'action')


@admin.register(UserTimeLine)
class UserTimeLineAdmin(admin.ModelAdmin):
    list_display = ('user__full_name', 'day',"start_time", "end_time")
    search_fields = ('user__full_name', 'day', 'start_time', 'end_time')
    list_filter = ('user__full_name', 'day', 'start_time', 'end_time')