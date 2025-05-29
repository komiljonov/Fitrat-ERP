from django.contrib import admin

from data.finances.compensation.models import Compensation, Bonus, Page, Asos, Monitoring, Point, Asos1_2, \
    MonitoringAsos1_2, ResultSubjects, ResultName


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


@admin.register(ResultSubjects)
class ResultSubjectsAdmin(admin.ModelAdmin):
    list_display = ("asos__name","name","result__name",'from_point','to_point','amount',"max_ball")
    search_fields = ("asos__name",'name')
    list_filter = ('asos__name',)

@admin.register(ResultName)
class ResultNameAdmin(admin.ModelAdmin):
    list_display = ("name","point_type",'who','type',)
    search_fields = ("name",'who')
    list_filter = ('name',)

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