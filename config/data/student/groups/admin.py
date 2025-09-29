from django.contrib import admin

from data.student.groups.models import Day, Group, Room, SecondaryGroup


# Register your models here.


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ("room_number", "room_filling")
    search_fields = ("room_number",)
    list_filter = ("room_number",)


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ("name", "teacher", "status", "room_number", "price")
    search_fields = ("name", "teacher", "status", "room_number", "price")


@admin.register(SecondaryGroup)
class SecondaryGroupAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "group__name",
        "status",
    )
    search_fields = (
        "name",
        "group__name",
        "status",
    )


@admin.register(Day)
class DayAdmin(admin.ModelAdmin):

    list_display = ["name", "display_name"]

    model = Day
