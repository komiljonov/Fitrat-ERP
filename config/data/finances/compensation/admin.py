from django.contrib import admin

from data.finances.compensation.models import Compensation, Bonus, Page, Asos, Monitoring


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


@admin.register(Asos)
class AsosAdmin(admin.ModelAdmin):
    list_display = ("name", 'max_ball',"created_at")
    search_fields = ("name",)

@admin.register(Monitoring)
class MonitoringAdmin(admin.ModelAdmin):
    list_display = ("user__full_name", 'asos',"ball")
    search_fields = ("name","user__full_name")
    list_filter = ('user__full_name',"ball")