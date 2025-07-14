from django.contrib import admin

from data.command.models import UserFilial


# Register your models here.

admin.site.unregister(UserFilial)
@admin.register(UserFilial)
class UserFilialAdmin(admin.ModelAdmin):
    list_display = ('id', 'user__full_name', 'filial__name')
    search_fields = ('user__full_name', 'filial__name')
    list_filter = ('user__full_name', 'filial__name')
