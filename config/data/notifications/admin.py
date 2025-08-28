from django.contrib import admin

from data.notifications.models import UserRFToken


# Register your models here.


@admin.register(UserRFToken)
class UserRFTokenAdmin(admin.ModelAdmin):
    list_display = ("user__phone", "token")
    list_filter = ("user__phone", "token")
    search_fields = ("user__phone", "token")
