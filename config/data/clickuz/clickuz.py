from .status import ORDER_FOUND, ORDER_NOT_FOUND, INVALID_AMOUNT
from django.conf import settings

class ClickUz:
    ORDER_FOUND = ORDER_FOUND
    ORDER_NOT_FOUND = ORDER_NOT_FOUND
    INVALID_AMOUNT = INVALID_AMOUNT

    def check_order(self, order_id: str, amount: str):
        from ..clickuz.models import Order
        student_order = Order.objects.filter(id=order_id).first()
        if not student_order:
            return ORDER_NOT_FOUND

        if str(student_order.amount) != str(amount):
            return INVALID_AMOUNT

        return ORDER_FOUND

    def successfully_payment(self, order_id: str, transaction: object):
        from ..clickuz.models import Order
        order = Order.objects.filter(id=order_id).first()
        if not order:
            return  # Optionally log this

        order.paid = True  # You must add this field to your `Order` model
        order.save()

        # Example: update balance
        if order.student and order.lid is None:
            order.student.balance = order.student.balance + float(order.amount)
            order.student.save()
        elif order.lid and order.student is None:
            order.lid.balance = order.lid.balance + float(order.amount)
            order.lid.save()

    def cancel_payment(self, order_id: str, transaction: object):
        from ..clickuz.models import Order

        order = Order.objects.filter(id=order_id).first()
        if not order:
            return


        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Cancelling Click payment for order {order_id}, transaction {transaction.id}")


        order.paid = False
        order.save()

    @staticmethod
    def generate_url(order_id, amount, return_url=None):
        service_id = settings.CLICK_SETTINGS['service_id']
        merchant_id = settings.CLICK_SETTINGS['merchant_id']
        url = f"https://my.click.uz/services/pay?service_id={service_id}&merchant_id={merchant_id}&amount={amount}&transaction_param={order_id}"
        if return_url:
            url += f"&return_url={return_url}"
        return url
