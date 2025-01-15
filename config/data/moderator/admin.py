from django.contrib import admin

from .models import Moderator


# Register your models here.
@admin.register(Moderator)
class ModeratorAdmin(admin.ModelAdmin):
    list_display = ('id', 'full_name', 'role')
    list_filter = ('role',)
