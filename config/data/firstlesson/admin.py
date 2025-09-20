from django.contrib import admin

from data.firstlesson.models import FirstLesson


# Register your models here.


@admin.register(FirstLesson)
class Admin(admin.ModelAdmin):

    list_display = [
        "lead",
        "group",
        "date",
        "status",
        "lesson_number",
        "is_archived",
        "comment",
        "creator",
    ]

    search_fields = [
        "lead__first_name",
        "lead__last_name",
        "lead__middle_name",
        "lead__phone_number",
    ]

    list_filter = ["status", "group"]

    date_hierarchy = "date"
