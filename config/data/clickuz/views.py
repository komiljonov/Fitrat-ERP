from rest_framework.views import APIView, Response

from . import ClickUz
from .models import Transaction
from rest_framework.permissions import AllowAny, IsAuthenticated
from .click_authorization import click_authorization
from .serializer import ClickUzSerializer, CreateOrderSerializer
from .status import *


class ClickUzMerchantAPIView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    VALIDATE_CLASS = None

    def post(self, request):

        print(request.data)

        serializer = ClickUzSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        METHODS = {
            PREPARE: self.prepare,
            COMPLETE: self.complete,
        }

        print("methods:", METHODS.items())

        merchant_trans_id = serializer.validated_data["merchant_trans_id"]
        amount = serializer.validated_data["amount"]
        action = serializer.validated_data["action"]

        if click_authorization(**serializer.validated_data) is False:
            return Response(
                {
                    "error": AUTHORIZATION_FAIL_CODE,
                    "error_note": AUTHORIZATION_FAIL,
                }
            )

        assert self.VALIDATE_CLASS != None
        check_order = self.VALIDATE_CLASS().check_order(
            order_id=merchant_trans_id, amount=amount
        )
        if check_order is True:
            result = METHODS[action](
                **serializer.validated_data,
                response_data=serializer.validated_data,
            )
            return Response(result)
        return Response(
            {
                "error": check_order,
                "error_note": {
                    ORDER_NOT_FOUND: "Order not found",
                    INVALID_AMOUNT: "Amount does not match",
                }.get(check_order, "Unknown error"),
            }
        )

    def prepare(
        self,
        click_trans_id: str,
        merchant_trans_id: str,
        amount: str,
        sign_string: str,
        sign_time: str,
        response_data: dict,
        *args,
        **kwargs
    ) -> dict:
        """

        :param click_trans_id:
        :param merchant_trans_id:
        :param amount:
        :param sign_string:
        :param response_data:
        :param args:
        :return:
        """
        transaction = Transaction.objects.create(
            click_trans_id=click_trans_id,
            merchant_trans_id=merchant_trans_id,
            amount=amount,
            action=PREPARE,
            sign_string=sign_string,
            sign_datetime=sign_time,
        )
        response_data.update(merchant_prepare_id=transaction.pk)
        return response_data

    def complete(
        self,
        click_trans_id,
        amount,
        error,
        merchant_prepare_id,
        response_data,
        action,
        *args,
        **kwargs
    ):
        """
        Handles the COMPLETE request from Click. Confirms or cancels the prepared transaction.

        :param click_trans_id: ID from Click system
        :param amount: Payment amount
        :param error: Error code sent by Click
        :param merchant_prepare_id: Local transaction ID (Transaction.pk)
        :param response_data: Initial validated serializer data
        :param action: Action type from Click (should be '1' for COMPLETE)
        :return: Response dictionary
        """
        from .status import (
            A_LACK_OF_MONEY,
            A_LACK_OF_MONEY_CODE,
            INVALID_AMOUNT,
            INVALID_ACTION,
            TRANSACTION_NOT_FOUND,
        )

        try:
            transaction = Transaction.objects.get(pk=merchant_prepare_id)

            # Case: Insufficient funds (Click error -5017)
            if error == A_LACK_OF_MONEY:
                self.VALIDATE_CLASS().cancel_payment(
                    transaction.merchant_trans_id, transaction
                )
                transaction.action = A_LACK_OF_MONEY
                transaction.status = Transaction.CANCELED
                transaction.save()
                response_data.update(error=A_LACK_OF_MONEY_CODE)
                return response_data

            # Case: Previously canceled due to insufficient funds
            if transaction.action == A_LACK_OF_MONEY:
                response_data.update(error=A_LACK_OF_MONEY_CODE)
                return response_data

            # Case: Amount mismatch (possible fraud or conflict)
            if str(transaction.amount) != str(amount):
                response_data.update(error=INVALID_AMOUNT)
                return response_data

            # Case: Duplicate COMPLETE call (action already set to COMPLETE)
            if (
                transaction.action == action
                or transaction.status == Transaction.FINISHED
            ):
                response_data.update(error=INVALID_ACTION)
                return response_data

            # All good → mark as finished
            transaction.action = action
            transaction.status = Transaction.FINISHED
            transaction.save()

            # Confirm payment in domain logic (balance update, flags, etc.)
            self.VALIDATE_CLASS().successfully_payment(
                transaction.merchant_trans_id, transaction
            )

            # Respond with success
            response_data.update(merchant_confirm_id=transaction.pk)
            return response_data

        except Transaction.DoesNotExist:
            response_data.update(error=TRANSACTION_NOT_FOUND)
            return response_data


class CreateClickOrderAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CreateOrderSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)

        order = serializer.save()

        payment_url = ClickUz.generate_url(order_id=order.id, amount=order.amount)

        return Response({"payment_url": payment_url})
