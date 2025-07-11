# payments/views.py
# django
from datetime import datetime
from decimal import Decimal

from django.conf import settings
from rest_framework import serializers
from rest_framework import status
from rest_framework.generics import ListCreateAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from data.paycomuz.methods_subscribe_api import PayComResponse  # your custom PayComResponse
from data.paycomuz.serializers import GeneratePaymentLinkSerializer
from . import Paycom
from .authentication import authentication
from .check_order import CheckOrder
# project
from .models import Transaction
from .serializers.payme_operation import PaycomOperationSerialzer
from .serializers.serializers import PaycomuzSerializer
from .status import *


class MerchantAPIView(APIView):
    permission_classes = [AllowAny]
    CHECK_PERFORM_TRANSACTION = 'CheckPerformTransaction'
    CREATE_TRANSACTION = 'CreateTransaction'
    PERFORM_TRANSACTION = 'PerformTransaction'
    CHECK_TRANSACTION = 'CheckTransaction'
    CANCEL_TRANSACTION = 'CancelTransaction'
    GET_STATEMENT = 'GetStatement'

    http_method_names = ['post']
    authentication_classes = []
    VALIDATE_CLASS: Paycom = None
    reply = None
    ORDER_KEY = KEY = settings.PAYCOM_SETTINGS['ACCOUNTS']['KEY']

    def __init__(self):
        self.METHODS = {
            self.CHECK_PERFORM_TRANSACTION: self.check_perform_transaction,
            self.CREATE_TRANSACTION: self.create_transaction,
            self.PERFORM_TRANSACTION: self.perform_transaction,
            self.CHECK_TRANSACTION: self.check_transaction,
            self.CANCEL_TRANSACTION: self.cancel_transaction,
            self.GET_STATEMENT: self.get_statement
        }

        self.REPLY_RESPONSE = {
            ORDER_FOUND: self.order_found,
            ORDER_NOT_FOUND: self.order_not_found,
            INVALID_AMOUNT: self.invalid_amount
        }

        super(MerchantAPIView, self).__init__()

    def post(self, request):
        check = authentication(request)
        if check is False or not check:
            return Response(AUTH_ERROR)
        serializer = PaycomOperationSerialzer(data=request.data, many=False)
        serializer.is_valid(raise_exception=True)
        method = serializer.validated_data['method']
        self.METHODS[method](serializer.validated_data)

        assert self.reply != None
        return Response(self.reply)

    def check_perform_transaction(self, validated_data):
        assert self.VALIDATE_CLASS is not None
        validate_class: Paycom = self.VALIDATE_CLASS()

        order_key = validated_data["params"]["account"].get(self.ORDER_KEY)

        result = validate_class.check_order(**validated_data["params"])
        if result != validate_class.ORDER_FOUND:
            self.reply = {
                "jsonrpc": "2.0",
                "id": validated_data["id"],
                "error": {
                    "code": validate_class.ORDER_NOT_FOUND,
                    "message": {
                        "uz": "Buyurtma topilmadi",
                        "ru": "Заказ не найден",
                        "en": "Order not found"
                    },
                    "data": None
                }
            }
            return

        amount = validated_data["params"].get("amount", 0)
        if amount <= 100000 or amount >= 999999999:
            return self.invalid_amount(validated_data)

        self.reply = {
            "jsonrpc": "2.0",
            "id": validated_data["id"],
            "result": {
                "allow": True
            }
        }

    def create_transaction(self, validated_data):
        order_key = validated_data['params']['account'].get(self.ORDER_KEY)
        if not order_key:
            raise serializers.ValidationError(f"{self.ORDER_KEY} required field")

        validate_class: Paycom = self.VALIDATE_CLASS()
        result = validate_class.check_order(**validated_data['params'])

        if result is None or result != ORDER_FOUND:
            self.reply = {
                "jsonrpc": "2.0",
                "id": validated_data["id"],
                "error": {
                    "code": ORDER_NOT_FOUND,
                    "message": ORDER_NOT_FOUND_MESSAGE,
                    "data": None
                }
            }
            return

        _id = validated_data['params']['id']
        amount = validated_data['params']['amount'] / 100
        now = int(datetime.now().timestamp() * 1000)

        existing_tx = Transaction.objects.filter(_id=_id).first()
        if existing_tx:
            self.reply = {
                "jsonrpc": "2.0",
                "id": validated_data["id"],
                "result": {
                    "create_time": int(existing_tx.created_datetime),
                    "transaction": str(existing_tx._id),
                    "state": existing_tx.state
                }
            }
            return

        # 🔥 Отключили автоотмену — это важно для песочницы
        # Никакие транзакции не отменяются автоматически

        tx = Transaction.objects.create(
            request_id=validated_data['id'],
            _id=_id,
            amount=amount,
            order_key=order_key,
            state=CREATE_TRANSACTION,
            created_datetime=now,
            status=Transaction.PROCESSING
        )

        self.reply = {
            "jsonrpc": "2.0",
            "id": validated_data["id"],
            "result": {
                "create_time": now,
                "transaction": str(tx._id),
                "state": CREATE_TRANSACTION
            }
        }

    def perform_transaction(self, validated_data):
        _id = validated_data['params']['id']
        request_id = validated_data['id']

        try:
            obj = Transaction.objects.get(_id=_id)

            if obj.state == CLOSE_TRANSACTION:
                self.reply = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "transaction": str(obj._id),
                        "perform_time": int(obj.perform_datetime),
                        "state": CLOSE_TRANSACTION
                    }
                }
                return

            if obj.state in [CANCEL_TRANSACTION_CODE, PERFORM_CANCELED_CODE]:
                obj.status = Transaction.FAILED
                obj.save()

                self.reply = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": UNABLE_TO_PERFORM_OPERATION,
                        "message": UNABLE_TO_PERFORM_OPERATION_MESSAGE,
                        "data": None
                    }
                }
                return

            if obj.state == CREATE_TRANSACTION:
                current_time = datetime.now()
                perform_time = int(current_time.timestamp() * 1000)

                obj.state = CLOSE_TRANSACTION
                obj.status = Transaction.SUCCESS
                obj.perform_datetime = perform_time

                self.VALIDATE_CLASS().successfully_payment(validated_data['params'], obj)
                obj.save()

                self.reply = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "transaction": str(obj._id),
                        "perform_time": perform_time,
                        "state": CLOSE_TRANSACTION
                    }
                }
                return

            # fallback
            self.reply = {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": UNABLE_TO_PERFORM_OPERATION,
                    "message": UNABLE_TO_PERFORM_OPERATION_MESSAGE,
                    "data": None
                }
            }

        except Transaction.DoesNotExist:
            self.reply = {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": TRANSACTION_NOT_FOUND,
                    "message": TRANSACTION_NOT_FOUND_MESSAGE,
                    "data": None
                }
            }

    def check_transaction(self, validated_data):
        _id = validated_data['params']['id']
        request_id = validated_data['id']

        try:
            transaction = Transaction.objects.get(_id=_id)

            self.reply = {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "create_time": int(transaction.created_datetime) if transaction.created_datetime else 0,
                    "perform_time": int(transaction.perform_datetime) if transaction.state == CLOSE_TRANSACTION else 0,
                    "cancel_time": 0 if transaction.state == CLOSE_TRANSACTION else int(
                        transaction.cancel_datetime or 0),
                    "transaction": str(transaction._id),
                    "state": transaction.state,
                    "reason": None if transaction.state == CLOSE_TRANSACTION else transaction.reason
                }
            }

        except Transaction.DoesNotExist:
            self.reply = {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": TRANSACTION_NOT_FOUND,
                    "message": TRANSACTION_NOT_FOUND_MESSAGE,
                    "data": None
                }
            }

    def cancel_transaction(self, validated_data):
        self.context_id = validated_data["id"]
        tx_id = validated_data['params']['id']
        reason = validated_data['params']['reason']

        try:
            transaction = Transaction.objects.get(_id=tx_id)

            now_ms = int(datetime.now().timestamp() * 1000)

            if transaction.state == CREATE_TRANSACTION:
                # ❗ Не выполнена, просто отменяем
                transaction.state = CANCEL_TRANSACTION_CODE  # -1
                transaction.status = Transaction.CANCELED
                transaction.reason = reason
                transaction.cancel_datetime = now_ms

            elif transaction.state == CLOSE_TRANSACTION:
                # ❗ Уже выполнена, требуется возврат
                transaction.state = PERFORM_CANCELED_CODE  # -2
                transaction.status = Transaction.CANCELED
                transaction.reason = reason
                transaction.cancel_datetime = now_ms

                # вызываем кастомный возврат
                self.VALIDATE_CLASS().cancel_payment(validated_data['params'], transaction)

            else:
                # ❌ уже отменена или что-то другое
                self.reply = {
                    "jsonrpc": "2.0",
                    "id": self.context_id,
                    "error": {
                        "code": UNABLE_TO_PERFORM_OPERATION,
                        "message": UNABLE_TO_PERFORM_OPERATION_MESSAGE,
                        "data": None
                    }
                }
                return

            transaction.save()
            self.response_check_transaction(transaction)

        except Transaction.DoesNotExist:
            self.reply = {
                "jsonrpc": "2.0",
                "id": self.context_id,
                "error": {
                    "code": TRANSACTION_NOT_FOUND,
                    "message": TRANSACTION_NOT_FOUND_MESSAGE,
                    "data": None
                }
            }


    def get_statement(self, validated_data):
        from_d = validated_data.get('params').get('from')
        to_d = validated_data.get('params').get('to')

        filtered_transactions = Transaction.objects.filter(
            created_datetime__gte=from_d,
            created_datetime__lte=to_d
        )

        transactions_json = [
            dict(
                id=obj._id,
                time=int(obj.created_datetime),
                amount=obj.amount,
                account=dict(
                    order_id=obj.order_key
                ),
                create_time=int(obj.created_datetime) if obj.created_datetime else 0,
                perform_time=int(obj.perform_datetime) if obj.perform_datetime else 0,
                cancel_time=int(obj.cancel_datetime) if obj.cancel_datetime else 0,
                transaction=obj.request_id,
                state=obj.state,
                reason=obj.reason,
            )

            for obj in filtered_transactions]

        response = dict(
            result=dict(
                transactions=transactions_json
            )
        )

        self.reply = response


    def order_found(self, validated_data):
        self.reply = dict(result=dict(allow=True))


    def order_not_found(self, validated_data):
        self.reply = dict(error=dict(
            id=validated_data['id'],
            code=ORDER_NOT_FOUND,
            message=ORDER_NOT_FOUND_MESSAGE
        ))


    def invalid_amount(self, validated_data):
        self.reply = {
            "jsonrpc": "2.0",
            "id": validated_data["id"],
            "error": {
                "code": INVALID_AMOUNT,  # usually -31001
                "message": INVALID_AMOUNT_MESSAGE,  # should be a dict with uz/ru/en
                "data": None
            }
        }


    def response_check_transaction(self, transaction: Transaction):
        self.reply = dict(result=dict(
            create_time=int(transaction.created_datetime) if transaction.created_datetime else 0,
            perform_time=int(transaction.perform_datetime) if transaction.perform_datetime else 0,
            cancel_time=int(transaction.cancel_datetime) if transaction.cancel_datetime else 0,
            transaction=str(transaction._id),
            state=transaction.state,
            reason=transaction.reason
        ))


class PaycomWebhookView(MerchantAPIView):
    VALIDATE_CLASS = CheckOrder


class TransactionAPIView(ListCreateAPIView):
    queryset = Transaction.objects.all()
    serializer_class = PaycomuzSerializer


class GeneratePaymeURLView(APIView):
    def post(self, request):
        print(request.data)

        # Correct way to access nested keys
        data = request.data.get("params", {})  # ✅ fix

        print(data)

        amount = data.get('amount')
        account = data.get('account', {})
        order_id = account.get('order_id')
        return_url = request.data.get("return_url", None)  # Optional

        print(amount, order_id, return_url)

        if not all([amount, order_id]):
            return Response({"detail": "Missing required fields."}, status=400)

        paycom = PayComResponse()
        url = paycom.create_initialization(
            amount=Decimal(amount),
            order_id=str(order_id),
            return_url=return_url
        )

        return Response({'payment_url': url}, status=status.HTTP_200_OK)
