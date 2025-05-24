from django.contrib import admin

from data.finances.compensation.models import Compensation, Bonus, Page, Asos, Monitoring, Point, Asos1_2, \
    MonitoringAsos1_2


@admin.register(Compensation)
class CompensationAdmin(admin.ModelAdmin):
    list_display = ("user__full_name","name", 'amount')
    search_fields = ("user__full_name","name",)


@admin.register(Bonus)
class BonsAdmin(admin.ModelAdmin):
    list_display = ("user__full_name","name", 'amount')
    search_fields = ("user__full_name","name",)


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ("user__phone", 'name','is_editable',"is_readable")
    search_fields = ("user__phone",'name')
    list_filter = ('is_editable','is_readable')


@admin.register(Asos)
class AsosAdmin(admin.ModelAdmin):
    list_display = ("name","created_at")
    search_fields = ("name",)


@admin.register(Point)
class PointAdmin(admin.ModelAdmin):
    list_display = ("name", 'asos__name',"max_ball","created_at")
    search_fields = ("name",)



@admin.register(Monitoring)
class MonitoringAdmin(admin.ModelAdmin):
    list_display = ("user__full_name","point__name" ,'point__max_ball',"ball")
    search_fields = ("name","user__full_name")
    list_filter = ('user__full_name',"ball")

@admin.register(Asos1_2)
class Asos1_2Admin(admin.ModelAdmin):
    list_display = ("asos","type" ,'amount',"ball")
    search_fields = ("asos",)
    list_filter = ('type',)

@admin.register(MonitoringAsos1_2)
class AsosAdmin(admin.ModelAdmin):
    list_display = ("user__full_name","asos","type" ,'amount',"ball")
    search_fields = ("user__full_name",)
    list_filter = ('type',)