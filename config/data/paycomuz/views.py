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
    authentication_classes = []
    http_method_names = ['post']

    CHECK_PERFORM_TRANSACTION = 'CheckPerformTransaction'
    CREATE_TRANSACTION = 'CreateTransaction'
    PERFORM_TRANSACTION = 'PerformTransaction'
    CHECK_TRANSACTION = 'CheckTransaction'
    CANCEL_TRANSACTION = 'CancelTransaction'
    GET_STATEMENT = 'GetStatement'

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
            self.GET_STATEMENT: self.get_statement,
        }

        self.REPLY_RESPONSE = {
            ORDER_FOUND: self.order_found,
            ORDER_NOT_FOUND: self.order_not_found,
            INVALID_AMOUNT: self.invalid_amount,
        }

        super(MerchantAPIView, self).__init__()

    def post(self, request):
        if not authentication(request):
            return Response(AUTH_ERROR)

        serializer = PaycomOperationSerialzer(data=request.data)
        serializer.is_valid(raise_exception=True)

        method = serializer.validated_data['method']
        self.METHODS[method](serializer.validated_data)
        assert self.reply is not None

        return Response(self.reply)

    def check_perform_transaction(self, validated_data):
        assert self.VALIDATE_CLASS is not None
        validate_class = self.VALIDATE_CLASS()
        result = validate_class.check_order(**validated_data['params'])

        if result == ORDER_FOUND:
            self.order_found(validated_data)
        else:
            self.order_not_found(validated_data)

    def create_transaction(self, validated_data):
        params = validated_data['params']
        order_key = params['account'].get(self.ORDER_KEY)
        if not order_key:
            raise serializers.ValidationError(f"{self.ORDER_KEY} required")

        validate_class = self.VALIDATE_CLASS()
        if validate_class.check_order(**params) != ORDER_FOUND:
            self.order_not_found(validated_data)
            return

        _id = params['id']
        amount = params['amount'] / 100
        now_ms = int(datetime.now().timestamp() * 1000)

        existing = Transaction.objects.filter(_id=_id).first()
        if existing:
            self.reply = {
                "jsonrpc": "2.0",
                "id": validated_data["id"],
                "result": {
                    "create_time": int(existing.created_datetime),
                    "transaction": str(existing._id),
                    "state": existing.state
                }
            }
            return

        other_tx = Transaction.objects.filter(
            order_key=order_key,
            status__in=[Transaction.PROCESSING, Transaction.SUCCESS]
        ).exclude(_id=_id).first()

        if other_tx:
            self.reply = {
                "jsonrpc": "2.0",
                "id": validated_data["id"],
                "error": {
                    "code": ON_PROCESS,
                    "message": {
                        "uz": "Buyurtma toʻlovi hozirda amalga oshirilmoqda",
                        "ru": "Платеж по заказу уже выполняется",
                        "en": "Payment for this order is already in process"
                    },
                    "data": None
                }
            }
            return

        tx = Transaction.objects.create(
            request_id=validated_data['id'],
            _id=_id,
            amount=amount,
            order_key=order_key,
            state=CREATE_TRANSACTION,
            created_datetime=now_ms,
            status=Transaction.PROCESSING
        )

        self.reply = {
            "jsonrpc": "2.0",
            "id": validated_data["id"],
            "result": {
                "create_time": now_ms,
                "transaction": str(tx._id),
                "state": CREATE_TRANSACTION
            }
        }

    def perform_transaction(self, validated_data):
        _id = validated_data['params']['id']
        request_id = validated_data['id']

        try:
            tx = Transaction.objects.get(_id=_id)

            if tx.status == Transaction.CANCELED or tx.state in [CANCEL_TRANSACTION_CODE, PERFORM_CANCELED_CODE]:
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

            if tx.state == self.PERFORM_TRANSACTION:
                self.response_check_transaction(tx)
                return

            now_ms = int(datetime.now().timestamp() * 1000)
            tx.state = self.PERFORM_TRANSACTION
            tx.status = Transaction.SUCCESS
            tx.perform_datetime = now_ms
            self.VALIDATE_CLASS().successfully_payment(validated_data['params'], tx)
            tx.save()

            self.reply = {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "transaction": str(tx._id),
                    "perform_time": now_ms,
                    "state": self.PERFORM_TRANSACTION
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
            tx = Transaction.objects.get(_id=_id)
            self.reply = {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "create_time": int(tx.created_datetime) if tx.created_datetime else 0,
                    "perform_time": int(tx.perform_datetime) if tx.perform_datetime else 0,
                    "cancel_time": int(tx.cancel_datetime) if tx.cancel_datetime else 0,
                    "transaction": str(tx._id),
                    "state": tx.state,
                    "reason": tx.reason if tx.reason is not None else None
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
        request_id = validated_data["id"]
        _id = validated_data["params"]["id"]
        reason = validated_data["params"]["reason"]

        try:
            tx = Transaction.objects.get(_id=_id)

            if tx.state == CREATE_TRANSACTION:
                tx.state = CANCEL_TRANSACTION_CODE
            elif tx.state == self.PERFORM_TRANSACTION:
                tx.state = PERFORM_CANCELED_CODE
                self.VALIDATE_CLASS().cancel_payment(validated_data['params'], tx)

            tx.status = Transaction.CANCELED
            tx.reason = reason
            tx.cancel_datetime = tx.cancel_datetime or int(datetime.now().timestamp() * 1000)
            tx.save()

            self.response_check_transaction(tx)

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

    def get_statement(self, validated_data):
        from_d = validated_data['params']['from']
        to_d = validated_data['params']['to']

        txs = Transaction.objects.filter(created_datetime__range=(from_d, to_d))

        self.reply = {
            "jsonrpc": "2.0",
            "id": validated_data["id"],
            "result": {
                "transactions": [
                    {
                        "id": tx._id,
                        "time": int(tx.created_datetime),
                        "amount": tx.amount,
                        "account": {"order_id": tx.order_key},
                        "create_time": int(tx.created_datetime),
                        "perform_time": int(tx.perform_datetime) if tx.perform_datetime else 0,
                        "cancel_time": int(tx.cancel_datetime) if tx.cancel_datetime else 0,
                        "transaction": tx.request_id,
                        "state": tx.state,
                        "reason": tx.reason
                    } for tx in txs
                ]
            }
        }

    def response_check_transaction(self, tx: Transaction):
        self.reply = {
            "jsonrpc": "2.0",
            "id": self.context_id if hasattr(self, "context_id") else tx.request_id,
            "result": {
                "create_time": int(tx.created_datetime) if tx.created_datetime else 0,
                "perform_time": int(tx.perform_datetime) if tx.perform_datetime else 0,
                "cancel_time": int(tx.cancel_datetime) if tx.cancel_datetime else 0,
                "transaction": str(tx._id),
                "state": tx.state,
                "reason": tx.reason
            }
        }

    def order_found(self, validated_data):
        self.reply = {"result": {"allow": True}}

    def order_not_found(self, validated_data):
        self.reply = {
            "jsonrpc": "2.0",
            "id": validated_data["id"],
            "error": {
                "code": ORDER_NOT_FOUND,
                "message": ORDER_NOT_FOUND_MESSAGE,
                "data": None
            }
        }

    def invalid_amount(self, validated_data):
        self.reply = {
            "jsonrpc": "2.0",
            "id": validated_data["id"],
            "error": {
                "code": INVALID_AMOUNT,
                "message": INVALID_AMOUNT_MESSAGE,
                "data": None
            }
        }


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
