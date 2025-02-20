from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from ..account.models import CustomUser
from ..account.forms import CustomUserChangeForm, CustomUserCreationForm


class CustomUserAdmin(UserAdmin):
    form = CustomUserChangeForm,CustomUserCreationForm
    model = CustomUser
    list_display = ("phone", "is_staff", "is_active",)
    list_filter = ("phone", "is_staff", "is_active",)
    fieldsets = (
        (None, {"fields": ("phone", "password")}),
        ("Personal Info", {"fields": ("name", "phone")}),

        ("Permissions", {"fields": ("is_staff", "is_active")}),
        ("Important dates", {"fields": ("created_at", "updated_at")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "phone", "password1", "is_staff",
                "is_active", "name", "phone","confirmation_code"

            )}
        ),
    )
    search_fields = ("phone", "name",)
    ordering = ("phone",)

    change_form_template = 'admin/auth/user/user_change_form.html'

admin.site.register(CustomUser)



