from decimal import Decimal

from django.db.models.signals import post_save
from django.dispatch import receiver

from data.finances.finance.choices import FinanceKindTypeChoices

from .models import Finance, VoucherStudent, Casher, Kind, KpiFinance
from data.logs.models import Log


@receiver(post_save, sender=Finance)
def on_create(sender, instance: Finance, created, **kwargs):
    if created:
        if instance.lid:
            if instance.action == "INCOME":
                instance.lid.balance += Decimal(instance.amount)
                instance.lid.save()

        # if instance.student and not instance.kind.name == "Lesson payment":
        if (
            instance.student
            and not instance.kind.kind == FinanceKindTypeChoices.LESSON_PAYMENT
        ):
            if instance.action == "INCOME":
                instance.student.balance += Decimal(instance.amount)
                instance.student.save()
            else:
                # if not instance.kind.name == "Voucher":
                if not instance.kind.kind == FinanceKindTypeChoices.VOUCHER:
                    instance.student.balance -= Decimal(instance.amount)
                    instance.student.save()

        if instance.stuff:
            if (
                instance.action == "EXPENSE"
                and instance.kind is not None
                # and instance.kind.name == "Salary"
                and instance.kind.kind == FinanceKindTypeChoices.SALARY
            ):
                instance.stuff.balance -= Decimal(instance.amount)
                instance.stuff.save()
            else:
                # if instance.kind.name != "Lesson payment":
                if instance.kind.kind != FinanceKindTypeChoices.LESSON_PAYMENT:
                    instance.stuff.balance += Decimal(instance.amount)
                    instance.stuff.save()


@receiver(post_save, sender=Finance)
def on_finance_create(sender, instance: Finance, created, **kwargs):
    if created:
        Log.objects.create(
            app="Finance",
            model="Finance",
            action="Finance",
            model_action="Created",
            finance=Finance.objects.filter(id=instance.id).first(),
            lid=instance.lid,
            student=instance.student,
            account=instance.stuff,
        )
        print("Log for finance created ...")

    if not created:
        Log.objects.create(
            app="Finance",
            model="Finance",
            action="Finance",
            model_action="Updated",
            finance=Finance.objects.filter(id=instance.id).first(),
            lid=instance.lid,
            student=instance.student,
            account=instance.stuff,
        )
        print("Log for finance updated ...")


@receiver(post_save, sender=VoucherStudent)
def on_create(sender, instance: VoucherStudent, created, **kwargs):
    if created:

        if instance.voucher:
            # Count the number of VoucherStudent objects for the given voucher
            voucher_student_count = VoucherStudent.objects.filter(
                voucher=instance.voucher
            ).count()

            if voucher_student_count >= instance.voucher.count:
                instance.voucher.is_expired = True
                instance.voucher.save()

        cashier = Casher.objects.filter(
            filial__in=instance.creator.filial.all(),
            role__in=["ADMINISTRATOR", "ACCOUNTANT"],
        ).first()

        if instance.lid:
            finance = Finance.objects.create(
                casher=cashier,
                action="EXPENSE",
                amount=instance.voucher.amount,
                # kind=Kind.objects.filter(name="Voucher").first(),
                kind=Kind.get(FinanceKindTypeChoices.VOUCHER),
                payment_method="Cash",
                lid=instance.lid,
                comment=f"Ushbu buyurtma uchun {instance.voucher.amount} so'm miqdorida voucher qo'shildi!",
            )
            finance.lid.balance += Decimal(finance.amount)
            finance.lid.save()

        else:
            finance = Finance.objects.create(
                casher=cashier,
                action="EXPENSE",
                amount=instance.voucher.amount,
                # kind=Kind.objects.filter(name="Voucher").first(),
                kind=Kind.get(FinanceKindTypeChoices.VOUCHER),
                payment_method="Cash",
                student=instance.student,
                comment=f"Ushbu o'quvchi uchun {instance.voucher.amount} so'm miqdorida voucher qo'shildi!",
            )
            finance.student.balance += Decimal(finance.amount)
            finance.student.save()


@receiver(post_save, sender=KpiFinance)
def on_create(sender, instance: KpiFinance, created, **kwargs):
    if created:
        if instance.type == "INCOME":
            # instance.user.balance += Decimal(instance.amount)
            # instance.user.save()

            Finance.objects.create(
                casher=Casher.objects.filter(
                    filial__in=instance.user.filial.all(),
                    role__in=["ADMINISTRATOR", "ACCOUNTANT"],
                ).first(),
                action="EXPENSE",
                amount=instance.amount,
                # kind=Kind.objects.filter(name="Bonus").first(),
                kind=Kind.get(FinanceKindTypeChoices.BONUS),
                stuff=instance.user,
                # comment = "Xodim uchun bonus sifatida qo'shildi!"
                comment=instance.reason,
            )
        else:

            # instance.user.balance -= Decimal(instance.amount)
            # instance.user.save()

            Finance.objects.create(
                casher=Casher.objects.filter(
                    filial__in=instance.user.filial.all(),
                    role__in=["ADMINISTRATOR", "ACCOUNTANT"],
                ).first(),
                action="INCOME",
                amount=instance.amount,
                # kind=Kind.objects.filter(name="Money back").first(),
                kind=Kind.get(FinanceKindTypeChoices.MONEY_BACK),
                stuff=instance.user,
                comment="Xodim uchun jarima sifatida qo'shildi!",
            )
