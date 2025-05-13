from django.contrib import admin
from .models import StudentGroup, SecondaryStudentGroup


# Register your models here.
@admin.register(StudentGroup)
class StudentGroupAdmin(admin.ModelAdmin):
    list_display = ('group','student','lid')
    search_fields = ('group','student','lid')
    list_filter = ('group',)


@admin.register(SecondaryStudentGroup)
class StudentGroupAdmin(admin.ModelAdmin):
    list_display = ('group__name','student__first_name','lid__first_name')
    search_fields = ('group__name','student__first_name','lid__first_name')
    list_filter = ('group__name',)
