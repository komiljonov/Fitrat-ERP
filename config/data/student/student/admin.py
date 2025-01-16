from django.contrib import admin

from .models import Student


# Register your models here.
@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ( 'first_name', 'last_name','phone_number')
    search_fields = ('first_name', 'last_name','phone_number')
    list_filter = ('first_name', 'last_name','phone_number')
