from django.contrib import admin

from .models import Finance, SaleStudent


# Register your models here.

@admin.register(Finance)
class FinansAdmin(admin.ModelAdmin):
    list_display = ("casher__name", "casher__role","action",'amount','kind')
    search_fields = ("action",'kind',)
    list_filter = ("action",'kind',)


@admin.register(SaleStudent)
class SaleStudentAdmin(admin.ModelAdmin):
    list_display = ("creator__full_name","sale__name","sale__amount","expire_date", "comment", "created_at")
    search_fields = ("sale__name","sale__amount")
    list_filter = ("sale__amount",)