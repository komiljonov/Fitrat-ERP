from django.contrib import admin

from data.student.homeworks.models import Homework, Homework_history
from data.student.student.models import Student


# Register your models here.

@admin.register(Homework)
class HomeworkAdmin(admin.ModelAdmin):
    list_display = ('title', 'choice',"created_at")
    list_filter = ('title',)
    search_fields = ('title',)


@admin.register(Homework_history)
class HomeworkHistoryAdmin(admin.ModelAdmin):
    list_display = ("homework__title", "student__fist_name","status","is_active","mark")
    list_filter = ('homework__title',"status","is_active")
    search_fields = ('homework__title',)