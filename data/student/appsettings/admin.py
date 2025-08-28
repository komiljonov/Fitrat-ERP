from django.contrib import admin

from data.student.appsettings.models import Store


# Register your models here.

@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ('text','has_expired', 'expired_date')
    list_filter = ('has_expired', 'expired_date')
    search_fields = ('text',)