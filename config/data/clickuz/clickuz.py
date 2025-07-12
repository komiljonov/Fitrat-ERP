from .status import ORDER_FOUND, ORDER_NOT_FOUND, INVALID_AMOUNT
from django.conf import settings

class ClickUz:
    ORDER_FOUND = ORDER_FOUND
    ORDER_NOT_FOUND = ORDER_NOT_FOUND
    INVALID_AMOUNT = INVALID_AMOUNT

    def check_order(self, order_id: str, amount: str):

        from ..lid.new_lid.models import Lid
        from ..student.student.models import Student

        """
        :Need to check order
        :param order_id:
        :param amount:
        :return: ORDER_NOT_FOUND or ORDER_FOUND or INVALID_AMOUNT
        """
        student_order = Student.objects.filter(id=order_id).first()
        if not student_order:
            return ORDER_NOT_FOUND

        lid_order = Lid.objects.filter(id=order_id).first()
        if not lid_order:
            return ORDER_NOT_FOUND

        return ORDER_FOUND

    def successfully_payment(self, order_id: str, transaction: object):
        """

        :param order_id:
        :return:
        """
        raise NotImplemented

    def cancel_payment(self, order_id: str, transaction: object):
        """
        ru: еще не добавлено отменить транзакцию
        en: not yet added cancel transaction
        :param order_id:
        :param transaction:
        :return:
        """
        pass

    @staticmethod
    def generate_url(order_id, amount, return_url=None):
        service_id = settings.CLICK_SETTINGS['service_id']
        merchant_id = settings.CLICK_SETTINGS['merchant_id']
        url = f"https://my.click.uz/services/pay?service_id={service_id}&merchant_id={merchant_id}&amount={amount}&transaction_param={order_id}"
        if return_url:
            url += f"&return_url={return_url}"
        return url
