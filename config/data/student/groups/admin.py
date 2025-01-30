from django.contrib import admin

from data.student.groups.models import Group, Room


# Register your models here.

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('room_number', 'room_filling')
    search_fields = ('room_number',)
    list_filter = ('room_number',)


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'teacher','status','room_number','price_type','price')
    search_fields = ('name','teacher','status','room_number','price_type','price')

