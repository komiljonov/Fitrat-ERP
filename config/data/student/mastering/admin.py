from django.contrib import admin

from .models import Mastering

# Register your models here.

@admin.register(Mastering)
class MasteringAdmin(admin.ModelAdmin):
    list_display = ('student__phone',"choice",'theme__title','test',"ball")
    search_fields = ('student__first_name',"choice",'lid__first_name','test__title',"ball")
    list_filter = ('student__first_name',"choice",'lid__first_name','test__title',"ball")
