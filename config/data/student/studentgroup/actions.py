from django.contrib import admin


@admin.action(description="Sync selected groups' price with their group")
def sync_group_price(modeladmin, request, queryset):
    for sg in queryset.select_related("group"):
        sg.price = sg.group.price
        sg.save(update_fields=["price"])
