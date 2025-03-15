from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Finance, SaleStudent


@receiver(post_save, sender=Finance)
def on_create(sender, instance: Finance, created, **kwargs):
    if created :
        if instance.student:
            if instance.action == "INCOME":
                instance.student.balance += instance.amount
                instance.student.save()
            else:
                instance.student.balance -= instance.amount
                instance.student.save()

        if instance.stuff:
            if instance.action == "EXPENSE" and (instance.kind.name == "Salary" or instance.kind.name == "Bonus"):
                instance.stuff.balance += instance.amount
                instance.stuff.save()
            else:
                instance.stuff.balance -= instance.amount
                instance.stuff.save()







