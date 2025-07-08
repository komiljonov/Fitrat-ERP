from django.contrib import admin

from data.student.shop.models import Coins
from data.student.student.models import Student


# Register your models here.
@admin.register(Coins)
class CoinsAdmin(admin.ModelAdmin):
    list_display = ('student__first_name', 'status', 'coin')
    search_fields = ('student__first_name',)
    list_filter = ('status',)