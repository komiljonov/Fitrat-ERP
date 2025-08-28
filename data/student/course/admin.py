from django.contrib import admin

from .models import Course

# Register your models here.
@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("name","subject","status")
    list_filter = ("status",)
    search_fields = ("name",)
    ordering = ("name",)
