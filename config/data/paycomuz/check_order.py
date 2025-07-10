# views.py
from data.lid.new_lid.models import Lid
from data.paycomuz import Paycom
from data.paycomuz.models import Transaction
from data.student.student.models import Student
from decimal import Decimal
from django.db import transaction as db_transaction

class CheckOrder(Paycom):
    def check_order(self, amount, account, *args, **kwargs):
        order_key = account.get("order_id")  # Must match `order_key` in Transaction

        order_id = order_key.get("order_id")

        print(account, order_key)

        if not order_key:
            return self.ORDER_NOT_FOUND

        # Check if order exists in Student or Lid
        student_exists = Student.objects.filter(id=order_key).exists()
        lead_exists = Lid.objects.filter(id=order_key).exists()

        if not (student_exists or lead_exists):
            return self.ORDER_NOT_FOUND

        return self.ORDER_FOUND

    def successfully_payment(self, account, transaction, *args, **kwargs):
        order_key = account.get("order_id")
        amount = Decimal(transaction.amount) / 100

        with db_transaction.atomic():
            # Credit balance
            student = Student.objects.filter(id=order_key).first()
            lead = Lid.objects.filter(id=order_key).first()
            user = student or lead
            if user:
                user.balance += amount
                user.save()

            # Update transaction
            Transaction.objects.update_or_create(
                _id=str(transaction.id),
                defaults={
                    "request_id": transaction.request_id,
                    "order_key": order_key,
                    "amount": amount,
                    "state": transaction.state,
                    "status": Transaction.SUCCESS,
                    "perform_datetime": transaction.perform_time,
                    "created_datetime": transaction.create_time,
                }
            )

    def cancel_payment(self, account, transaction, *args, **kwargs):
        order_key = account.get("order_id")
        Transaction.objects.update_or_create(
            _id=str(transaction.id),
            defaults={
                "request_id": transaction.request_id,
                "order_key": order_key,
                "amount": Decimal(transaction.amount) / 100,
                "state": transaction.state,
                "status": Transaction.CANCELED,
                "cancel_datetime": transaction.cancel_time,
                "reason": transaction.reason,
            }
        )
