from .methods_subscribe_api import PayComResponse


class Paycom(PayComResponse):
    ORDER_FOUND = 200
    ORDER_NOT_FOND = -31050
    INVALID_AMOUNT = -31001

    def check_order(self, amount, account, *args, **kwargs):
        """
        >>> self.check_order(amount=amount, account=account)
        """

        pass

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

    def is_nakopitelnaya(self, transaction) -> bool:
        """
        Return True if this is a flexible ('nakopitelnaya') account transaction.
        You can check this via metadata, transaction.order_type, or model field.
        """
        order = self.get_order_by_key(transaction.order_key)
        return getattr(order, 'is_flexible', False)

    def can_cancel_order(self, transaction) -> bool:
        """
        Return True if the fixed account transaction is cancelable.
        Could depend on time, delivery, attendance, etc.
        """
        order = self.get_order_by_key(transaction.order_key)
        return not order.state == 1 and not order.cancel_reason

    def mark_order_as_canceled(self, transaction):
        """
        Mark fixed account order as canceled.
        """
        order = self.get_order_by_key(transaction.order_key)
        order.is_canceled = True
        order.save()

    def get_order_by_key(self, order_key):
        from payme.models import PaymeTransactions
        return PaymeTransactions.objects.filter(order_id=order_key).first()