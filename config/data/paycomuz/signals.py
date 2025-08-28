from django.db.models.signals import post_save
from django.dispatch import receiver

from config.data.finances.finance.choices import FinanceKindTypeChoices
from data.finances.finance.models import Finance, Kind
from data.lid.new_lid.models import Lid
from data.paycomuz.models import Transaction
from data.student.student.models import Student


@receiver(post_save, sender=Transaction)
def on_pre_save(sender, instance: Transaction, created, **kwargs):

    if created and instance.state == "success":

        # kind = Kind.objects.filter(name="Lesson payment").first()
        kind, created = Kind.objects.get_or_create(
            kind=FinanceKindTypeChoices.LESSON_PAYMENT
        )

        student = Student.objects.filter(id=instance.order_key).first()
        lid = Lid.objects.filter(id=instance.order_key).first()

        finance = Finance.objects.create(
            action="INCOME",
            amount=instance.amount,
            kind=kind,
            creator=instance.creator,
            payment_method="Payme",
            student=student if student else None,
            lid=lid if lid else None,
            comment=f"{student.first_name + "  " + student.last_name if student else 
            lid.first_name + " " + lid.last_name} talabaga {instance.amount} so'm pul to'lov qilindi.",
        )

        if finance:
            print("finance --- ?")
