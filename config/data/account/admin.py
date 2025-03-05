from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from ..account.models import CustomUser
from ..account.forms import CustomUserChangeForm, CustomUserCreationForm


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    form = CustomUserChangeForm  # ✅ Assign a single form
    add_form = CustomUserCreationForm  # ✅ Separate form for adding users

    model = CustomUser
    list_display = ("first_name", "last_name", "phone", "role", "is_staff", "is_active")
    list_filter = ("role", "is_active")

    # ✅ Ensure each field appears only once
    fieldsets = (
        (None, {"fields": ("phone", "password")}),
        ("Personal Info", {"fields": ("name",)}),  # ✅ Removed duplicate "phone"
        ("Permissions", {"fields": ("is_staff", "is_active")}),
        ("Important dates", {"fields": ("created_at", "updated_at")}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("phone", "password1", "is_staff", "is_active", "name", "confirmation_code"),  # ✅ Removed duplicate "phone"
        }),
    )

    search_fields = ("phone", "name")
    ordering = ("phone",)  # ✅ Ensure ordering is valid

