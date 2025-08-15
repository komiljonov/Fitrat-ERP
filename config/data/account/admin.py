from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from rest_framework_simplejwt.token_blacklist import admin as blacklist_admin

from ..account.forms import CustomUserChangeForm, CustomUserCreationForm
from ..account.models import CustomUser


class CustomUserAdmin(UserAdmin):
    form = CustomUserChangeForm, CustomUserCreationForm
    model = CustomUser
    list_display = (
        "phone",
        "is_staff",
        "is_active",
    )
    list_filter = (
        "phone",
        "is_staff",
        "is_active",
    )
    fieldsets = (
        (None, {"fields": ("phone", "password")}),
        ("Personal Info", {"fields": ("name", "phone")}),
        ("Permissions", {"fields": ("is_staff", "is_active")}),
        ("Important dates", {"fields": ("created_at", "updated_at")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "phone",
                    "password1",
                    "is_staff",
                    "is_active",
                    "name",
                    "phone",
                    "calculate_penalties",
                ),
            },
        ),
    )
    search_fields = (
        "phone",
        "name",
    )
    ordering = ("phone",)

    change_form_template = "admin/auth/user/user_change_form.html"


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):

    list_display = ["full_name", "phone", "extra_number"]

    search_fields = ["phone", "extra_number", "full_name"]


# Remove token registration from blacklist's admin module
try:
    admin.site.unregister(blacklist_admin.OutstandingToken)
except admin.sites.NotRegistered:
    pass

try:
    admin.site.unregister(blacklist_admin.BlacklistedToken)
except admin.sites.NotRegistered:
    pass
