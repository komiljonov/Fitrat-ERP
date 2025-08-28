from django.contrib import admin

from .models import Student, FistLesson_data


# Register your models here.
@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ( 'first_name', 'last_name','phone',"student_stage_type")
    search_fields = ('first_name', 'last_name','phone')
    list_filter = ('first_name', 'last_name','phone',"student_stage_type")


@admin.register(FistLesson_data)
class FistLessonDataAdmin(admin.ModelAdmin):
    list_display = ( 'teacher__full_name', 'group__name','lesson_date',"lid__first_name")
    list_filter = ('teacher__full_name', 'group__name','lesson_date')
    search_fields = ('teacher__full_name', 'group__name','lesson_date')