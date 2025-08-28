from django.contrib import admin

from data.student.lesson.models import FirstLLesson


# Register your models here.


@admin.register(FirstLLesson)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('id', 'lid', 'date','time')
    list_filter = ( 'lid',)