from django.contrib import admin
from .models import StudentGroup
# Register your models here.
@admin.register(StudentGroup)
class StudentGroupAdmin(admin.ModelAdmin):
    list_display = ('group','student','lid')
    search_fields = ('group','student','lid')
    list_filter = ('group',)
