from django.contrib import admin

from .models import Theme

# Register your models here.
@admin.register(Theme)
class ThemeAdmin(admin.ModelAdmin):
    list_display = ('subject__name','title',"course__name","level")
    search_fields = ('subject','title',"course__name","level")
    list_filter = ('subject','title',"course","level")


