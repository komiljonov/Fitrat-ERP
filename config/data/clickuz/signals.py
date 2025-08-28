from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver

from data.finances.finance.choices import FinanceKindTypeChoices
from data.clickuz.models import Order
from data.finances.finance.models import Finance, Kind


@receiver(post_save, sender=Order)
def on_pre_save(sender, instance: Order, created, **kwargs):

    if not created and instance.paid == True:

        # kind = Kind.objects.filter(name="Lesson payment").first()

        kind = Kind.get(FinanceKindTypeChoices.LESSON_PAYMENT)

        finance = Finance.objects.create(
            action="INCOME",
            amount=instance.amount,
            kind=kind,
            payment_method="Click",
            creator=instance.creator,
            student=instance.student if instance.student else None,
            lid=instance.lid if instance.lid else None,
            comment=f"{instance.student.first_name + "  " + instance.student.last_name if instance.student else 
            instance.lid.first_name + " " + instance.lid.last_name} talabaga {instance.amount} so'm pul to'lov qilindi.",
        )

        if finance:
            print("finance --- ?")
