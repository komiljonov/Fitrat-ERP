from django.contrib import admin

from data.finances.compensation.models import Compensation, Bonus


# Register your models here.
@admin.register(Compensation)
class CompensationAdmin(admin.ModelAdmin):
    list_display = ("name", 'amount')
    search_fields = ("name",)


@admin.register(Bonus)
class BonsAdmin(admin.ModelAdmin):
    list_display = ("name", 'amount')
    search_fields = ("name",)
