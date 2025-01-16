from django.contrib import admin

from .models import Lid


# Register your models here.
@admin.register(Lid)
class LidAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'phone_number', 'filial','call_operator','lid_stage_type')
    search_fields = ('first_name', 'phone_number', 'filial','call_operator')
    list_filter = ('lid_stage_type','is_dubl','is_student','is_archived')

