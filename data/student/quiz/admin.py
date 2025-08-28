from django.contrib import admin

from data.student.quiz.models import ExamRegistration
from data.student.student.models import Student


# Register your models here.

@admin.register(ExamRegistration)
class ExamRegistrationAdmin(admin.ModelAdmin):
    list_display = ('student__first_name',"exam__date","exam__start_time","exam__end_time","mark")
    list_filter = ('student__first_name',)
    search_fields = ('student__first_name',)