from django.contrib import admin

from data.results.models import Results


# # Register your models here.
# @admin.register(Result)
# class ResultAdmin(admin.ModelAdmin):
#     list_display = ('results', 'teacher__full_name', 'student__first_name', 'student__last_name')
#     list_filter = ('results', 'teacher__full_name')
#     search_fields = ('results', 'teacher__full_name')