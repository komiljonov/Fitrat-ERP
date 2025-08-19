from django.contrib import admin

from .models import Casher, Finance, KpiFinance, SaleStudent


# Register your models here.


@admin.register(Finance)
class FinansAdmin(admin.ModelAdmin):
    list_display = (
        "lid__first_name",
        "student__first_name",
        "lid__lid_stage_type",
        "casher__role",
        "action",
        "amount",
        "kind",
        "created_at",
    )
    search_fields = (
        "action",
        "kind",
    )
    list_filter = (
        "action",
        "kind",
        "filial",
        "student"
    )


@admin.register(SaleStudent)
class SaleStudentAdmin(admin.ModelAdmin):
    list_display = (
        "creator__full_name",
        "sale__name",
        "sale__amount",
        "expire_date",
        "comment",
        "created_at",
    )
    search_fields = ("sale__name", "sale__amount")
    list_filter = ("sale__amount",)


@admin.register(KpiFinance)
class KpiFinanceAdmin(admin.ModelAdmin):

    list_display = ["user", "lid", "student", "reason", "amount", "type"]

    list_filter = ["user", "student"]

    search_fields = ["user__full_name", "user__phone"]


@admin.register(Casher)
class CasherAdmin(admin.ModelAdmin):

    list_display = ["name", "filial", "user", "role", "is_archived"]

    search_fields = ["name", "user__full_name", "role"]

    list_filter = ["role", "is_archived"]
