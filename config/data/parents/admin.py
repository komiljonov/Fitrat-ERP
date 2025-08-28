from django.contrib import admin


from .models import Relatives


@admin.register(Relatives)
class RelativeAdmin(admin.ModelAdmin):

    list_display = ["name", "phone", "who", "lid", "student", "user"]

    search_fields = ["name", "phone", "who"]

    model = Relatives
