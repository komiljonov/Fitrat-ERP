from django.contrib import admin

from data.student.groups.models import Day, Group, Room, SecondaryGroup
from data.student.subject.models import Theme


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

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "start_theme":
            obj = getattr(request, "_obj_", None)
            qs = Theme.objects.filter(is_archived=False)
            if obj and obj.level_id:
                qs = qs.filter(level_id=obj.level_id)
            if obj and obj.course_id:
                qs = qs.filter(course_id=obj.course_id)
            kwargs["queryset"] = qs
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_object(self, request, object_id, from_field=None):
        obj = super().get_object(request, object_id, from_field)
        request._obj_ = obj
        return obj


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
