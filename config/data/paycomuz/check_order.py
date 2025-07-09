# views.py
from data.lid.new_lid.models import Lid
from data.paycomuz import Paycom
from data.student.student.models import Student
from decimal import Decimal
from django.db import transaction as db_transaction

class CheckOrder(Paycom):
    def check_order(self, amount, account, *args, **kwargs):
        order_id = account.get("order_id")
        if not order_id:
            return self.ORDER_NOT_FOUND

        if Student.objects.filter(id=order_id).exists() or Lid.objects.filter(id=order_id).exists():
            return self.ORDER_FOUND
        return self.ORDER_NOT_FOUND

    def successfully_payment(self, account, transaction, *args, **kwargs):
        order_id = account.get("order_id")
        amount = Decimal(transaction.amount) / 100  # Payme sends tiyin (smallest unit)

        with db_transaction.atomic():
            # Try updating Student
            student = Student.objects.filter(id=order_id).first()
            if student:
                student.balance += amount
                student.save()
                print(f"✅ Paid {amount} to Student {student.id}")
                return

            # Try updating Lid
            lead = Lid.objects.filter(id=order_id).first()
            if lead:
                lead.balance += amount
                lead.save()
                print(f"✅ Paid {amount} to Lid {lead.id}")
                return

            print(f"❌ No Student or Lid found with ID {order_id}")

    def cancel_payment(self, account, transaction, *args, **kwargs):
        print(f"❌ Payment cancelled for order_id={account.get('order_id')} | transaction={transaction.id}")
