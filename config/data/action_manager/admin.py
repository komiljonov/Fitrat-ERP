from django.contrib import admin

from .models import ActionLogCustom

# Check if the model is already registered
if not admin.site.is_registered(ActionLogCustom):
    @admin.register(ActionLogCustom)
    class ActionLogCustomAdmin(admin.ModelAdmin):
        list_display = ('user', 'action', 'endpoint', 'method', 'status_code', 'timestamp')
        list_filter = ('action', 'method', 'status_code')
        search_fields = ('user__username', 'endpoint', 'request_data', 'response_data')
