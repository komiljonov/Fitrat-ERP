from django.contrib import admin

from data.finances.compensation.models import Compensation, Bonus, Page


# Register your models here.
@admin.register(Compensation)
class CompensationAdmin(admin.ModelAdmin):
    list_display = ("name", 'amount')
    search_fields = ("name",)


@admin.register(Bonus)
class BonsAdmin(admin.ModelAdmin):
    list_display = ("name", 'amount')
    search_fields = ("name",)


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ("user__phone", 'name','is_editable',"is_readable")
    search_fields = ("user__phone",'name')
    list_filter = ('is_editable','is_readable')
