from django.contrib import admin

from .models import Finance


# Register your models here.

@admin.register(Finance)
class FinansAdmin(admin.ModelAdmin):
    list_display = ("casher__name", "casher__role","action",'amount','kind')
    search_fields = ("action",'kind',)
    list_filter = ("action",'kind',)
