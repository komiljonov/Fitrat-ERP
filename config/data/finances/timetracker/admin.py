from django.contrib import admin

from .models import Employee_attendance


# Register your models here.


@admin.register(Employee_attendance)
class FinansAdmin(admin.ModelAdmin):
    list_display = ('user__full_name', 'action','is_there',"is_gone")
    search_fields = ('user__full_name', 'action')
    list_filter = ('user__full_name', 'action','is_there',"is_gone")

