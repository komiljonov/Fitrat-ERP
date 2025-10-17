from django.contrib import admin

# Register your models here.

from data.student.transactions.models import StudentTransaction

@admin.register(StudentTransaction)
class StudentTransactionAdmin(admin.ModelAdmin):
    list_display = ["created_by", "reason", "amount", "effective_amount"]
    readonly_fields = ["effective_amount"]