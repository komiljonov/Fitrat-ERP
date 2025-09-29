from django.contrib import admin
from rangefilter.filters import DateRangeFilter

from .models import Attendance, SecondaryAttendance


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = (
        "date",
        "student_info",
        "lead",
        "group",
        "status",
        "created_at",
    )

    list_filter = ("status", ("created_at", DateRangeFilter), "group", "student_group")

    search_fields = (
        "status",
        "group__name",
        "lead__first_name",
        "student__first_name",
        "student__phone",
    )

    ordering = ("-created_at",)

    date_hierarchy = "created_at"

    readonly_fields = ("created_at", "updated_at")

    def student_info(self, obj):
        if obj.student:
            return f"{obj.student.first_name} {obj.student.last_name} ({obj.student.phone})"
        return "-"

    student_info.short_description = "Student Info"


@admin.register(SecondaryAttendance)
class SecondaryAttendanceAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "student_info",
        "group",
        "theme",
        "status",
        "created_at",
        "updated_at",
    )
    list_filter = (
        "status",
        ("created_at", DateRangeFilter),
        "group",
    )
    search_fields = (
        "status",
        "student__first_name",
        "student__last_name",
        "student__phone",
    )
    ordering = ("-created_at",)
    date_hierarchy = "created_at"
    readonly_fields = ("created_at", "updated_at")
    actions = ["mark_as_absent", "mark_as_present", "export_selected"]

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "student",
                    "group",
                    "theme",
                    "status",
                    "comment",
                ),
            },
        ),
        (
            "Timestamps",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    def student_info(self, obj):
        if obj.student:
            return f"{obj.student.first_name} {obj.student.last_name} ({obj.student.phone})"
        return "-"

    student_info.short_description = "Student Info"

    def mark_as_absent(self, request, queryset):
        updated = queryset.update(status="IS_ABSENT")
        self.message_user(request, f"{updated} entries marked as absent.")

    mark_as_absent.short_description = "Mark selected as Absent"

    def mark_as_present(self, request, queryset):
        updated = queryset.update(status="IS_PRESENT")
        self.message_user(request, f"{updated} entries marked as present.")

    mark_as_present.short_description = "Mark selected as Present"

    def export_selected(self, request, queryset):
        # You can implement CSV export logic here if needed
        self.message_user(
            request, f"{queryset.count()} records exported (fake action)."
        )

    export_selected.short_description = "Export selected entries"
