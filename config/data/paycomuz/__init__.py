from .methods_subscribe_api import PayComResponse
from ..lid.new_lid.models import Lid
from ..student.student.models import Student


class Paycom(PayComResponse):
    ORDER_FOUND = 200
    ORDER_NOT_FOND = -31050
    INVALID_AMOUNT = -31001

    def check_order(self, amount, account, *args, **kwargs):
        """
        >>> self.check_order(amount=amount, account=account)
        """
        order_key = account.get("order_id")  # Must match `order_key` in Transaction

        if not order_key:
            return self.ORDER_NOT_FOUND

        # Check if order exists in Student or Lid
        student_exists = Student.objects.filter(id=order_key).exists()
        lead_exists = Lid.objects.filter(id=order_key).exists()

        if not (student_exists or lead_exists):
            return self.ORDER_NOT_FOUND

        return self.ORDER_FOUND

    def successfully_payment(self, account, transaction, *args, **kwargs):
        """
        >>> self.successfully_payment(account=account, transaction=transaction)
        """
        pass

    def cancel_payment(self, account, transaction, *args, **kwargs):
        """
        >>> self.cancel_payment(account=account,transaction=transaction)
        """
        pass
