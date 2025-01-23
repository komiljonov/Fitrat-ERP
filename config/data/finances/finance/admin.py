from django.contrib import admin

from .models import Finance


# Register your models here.

@admin.register(Finance)
class FinansAdmin(admin.ModelAdmin):
    list_display = ('student','stuff', "action",'amount','kind')
    search_fields = ("action",'kind',)
    list_filter = ("action",'kind',)
