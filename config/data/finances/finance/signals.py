from itertools import count

from django.db.models import Count
from django.db.models.signals import post_save
from django.dispatch import receiver
from icecream import ic

from .models import Finance, SaleStudent, Voucher, VoucherStudent, Casher, Kind, PaymentMethod, KpiFinance


@receiver(post_save, sender=Finance)
def on_create(sender, instance: Finance, created, **kwargs):
    if created :
        if instance.lid :
            if instance.action == "INCOME":
                instance.lid.balance+= instance.amount
                instance.lid.save()


        if instance.student:
            if instance.action == "INCOME":
                instance.student.balance += instance.amount
                instance.student.save()
            else:
                if not instance.kind.name == "Voucher":
                    instance.student.balance -= instance.amount
                    instance.student.save()

        if instance.stuff:
            if instance.action == "EXPENSE" and (instance.kind.name == "Salary" or instance.kind.name == "Bonus"):
                instance.stuff.balance -= instance.amount
                instance.stuff.save()
            else:
                instance.stuff.balance += instance.amount
                instance.stuff.save()





@receiver(post_save, sender=VoucherStudent)
def on_create(sender, instance: VoucherStudent, created, **kwargs):
    if created:

        if instance.voucher:
            # Count the number of VoucherStudent objects for the given voucher
            voucher_student_count = VoucherStudent.objects.filter(voucher=instance.voucher).count()

            if voucher_student_count >= instance.voucher.count:
                instance.voucher.is_expired = True
                instance.voucher.save()
        casher = Casher.objects.filter(filial__in=instance.creator.filial.all(),
                                       role__in=["ADMINISTRATOR", "ACCOUNTANT"]).first()
        if instance.lid:
            finance = Finance.objects.create(
                casher = casher,
                action = "EXPENSE",
                amount = instance.voucher.amount,
                kind = Kind.objects.filter(name="Voucher").first(),
                payment_method="Cash",
                lid=instance.lid,
                comment = f"Ushbu buyurtma uchun {instance.voucher.amount} so'm miqdorida voucher qo'shildi!"
            )
            finance.lid.balance += finance.amount
            finance.lid.save()

        else:
            finance = Finance.objects.create(
                casher=casher,
                action="EXPENSE",
                amount=instance.voucher.amount,
                kind=Kind.objects.filter(name="Voucher").first(),
                payment_method="Cash",
                student=instance.student,
                comment= f"Ushbu o'quvchi uchun {instance.voucher.amount} so'm miqdorida voucher qo'shildi!"
            )
            finance.student.balance += finance.amount
            finance.student.save()


        ic(f"For {finance.lid.first_name if finance.lid else finance.student.first_name} voucher created ...")



@receiver(post_save, sender=KpiFinance)
def on_create(sender, instance: KpiFinance, created, **kwargs):
    if created:
        instance.user.balance += instance.amount
        instance.user.save()

