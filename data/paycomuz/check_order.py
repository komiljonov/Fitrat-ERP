# views.py
from datetime import datetime
from decimal import Decimal

from django.db import transaction as db_transaction
from rest_framework import serializers

from data.lid.new_lid.models import Lid
from data.paycomuz import PayComResponse
from data.paycomuz.models import Transaction
from data.student.student.models import Student


class CheckOrder(PayComResponse):
    ORDER_FOUND = 200
    ORDER_NOT_FOUND = -31050
    ON_PROCESS = -31099
    CREATE_TRANSACTION = 0
    ORDER_KEY = "order_id"

    def check_order(self, amount, account, *args, **kwargs):
        order_key = account.get(self.ORDER_KEY)

        if not order_key:
            return self.ORDER_NOT_FOUND

        # Check in both Student and Lid
        if Student.objects.filter(id=order_key).exists():
            return self.ORDER_FOUND
        if Lid.objects.filter(id=order_key).exists():
            return self.ORDER_FOUND

        return self.ORDER_NOT_FOUND

    def create_transaction(self, validated_data):
        order_key = validated_data['params']['account'].get(self.ORDER_KEY)

        print("order_key",order_key)

        if not order_key:
            raise serializers.ValidationError(f"{self.ORDER_KEY} required field")

        print("waiting result")
        result = self.check_order(**validated_data['params'])

        print(result)
        print("----------")

        if result != self.ORDER_FOUND:
            self.reply = dict(error=dict(
                id=validated_data['id'],
                code=self.ORDER_NOT_FOUND,
                message={
                    "uz": "Buyurtma topilmadi",
                    "ru": "Заказ не найден",
                    "en": "Order not found"
                }
            ))
            return

        _id = validated_data['params']['id']
        amount = validated_data['params']['amount'] / 100
        request_id = validated_data['id']
        current_time_ms = int(datetime.now().timestamp() * 1000)

        print(_id,amount,request_id,current_time_ms)

        existing_tx = Transaction.objects.filter(_id=_id).first()

        print(existing_tx)

        if existing_tx:
            # Return existing transaction info
            self.reply = dict(result=dict(
                create_time=existing_tx.created_datetime,
                transaction=str(existing_tx._id),
                state=existing_tx.state,
            ))
            return

        # Check if there's another transaction for this order_key in progress
        previous_tx = Transaction.objects.filter(order_key=order_key, status=Transaction.PROCESSING).exclude(
            _id=_id).first()

        print(previous_tx)

        tx, created = Transaction.objects.get_or_create(
            _id=_id,
            defaults={
                "request_id": request_id,
                "amount": amount,
                "order_key": order_key,
                "state": self.CREATE_TRANSACTION,
                "created_datetime": current_time_ms,
                "status": Transaction.PROCESSING,
            }
        )

        if previous_tx:
            self.reply = dict(error=dict(
                id=request_id,
                code=self.ON_PROCESS,
                message={
                    "uz": "Buyurtma to'lo'vi hozirda amalga oshirilmoqda",
                    "ru": "Платеж на этот заказ на данный момент в процессе",
                    "en": "Payment for this order is currently on process"
                }
            ))
            return

        obj = Transaction.objects.create(
            request_id=request_id,
            _id=_id,
            amount=amount,
            order_key=order_key,
            state=self.CREATE_TRANSACTION,
            created_datetime=current_time_ms,
            status=Transaction.SUCCESS,
        )

        print(obj)

        self.reply = dict(result=dict(
            create_time=current_time_ms,
            transaction=str(obj._id),
            state=self.CREATE_TRANSACTION
        ))

    def successfully_payment(self, account, transaction, *args, **kwargs):
        order_key = account.get(self.ORDER_KEY)
        amount = Decimal(transaction.amount)

        with db_transaction.atomic():
            user = Student.objects.filter(id=order_key).first() or Lid.objects.filter(id=order_key).first()
            if user:
                user.balance += amount
                user.save()

            Transaction.objects.update_or_create(
                _id=str(transaction._id),
                defaults={
                    "request_id": transaction.request_id,
                    "order_key": order_key,
                    "amount": amount,
                    "state": transaction.state,
                    "status": Transaction.SUCCESS,
                    "perform_datetime": transaction.perform_datetime,
                    "created_datetime": transaction.created_datetime,
                }
            )

    def cancel_payment(self, account, transaction, *args, **kwargs):
        order_key = account.get(self.ORDER_KEY)

        Transaction.objects.update_or_create(
            _id=str(transaction._id),
            defaults={
                "request_id": transaction.request_id,
                "order_key": order_key,
                "amount": Decimal(transaction.amount),
                "state": transaction.state,
                "status": Transaction.CANCELED,
                "cancel_datetime": transaction.cancel_datetime,
                "reason": transaction.reason,
            }
        )
