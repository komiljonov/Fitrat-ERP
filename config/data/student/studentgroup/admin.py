from django.contrib import admin
from .models import StudentGroup, SecondaryStudentGroup


# Register your models here.
@admin.register(StudentGroup)
class StudentGroupAdmin(admin.ModelAdmin):
    list_display = ("group", "student", "lid", "is_archived", "created_at")
    search_fields = (
        "group",
        "student__first_name",
        "student__last_name",
        "student__middle_name",
        "lid__first_name",
        "lid__last_name",
        "lid__middle_name",
    )
    list_filter = ("group", "group__teacher", "is_archived", "student")


@admin.register(SecondaryStudentGroup)
class StudentGroupAdmin(admin.ModelAdmin):
    list_display = ("group__name", "student__first_name", "lid__first_name")
    search_fields = ("group__name", "student__first_name", "lid__first_name")
    list_filter = ("group__name",)
