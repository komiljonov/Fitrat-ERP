from django.contrib import admin

from .models import Theme

# Register your models here.
@admin.register(Theme)
class ThemeAdmin(admin.ModelAdmin):
    list_display = ('subject','title','type')
    search_fields = ('subject','title')
    list_filter = ('type',)
    ordering = ('type',)

