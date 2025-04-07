import datetime
from decimal import Decimal

from django.db.models.signals import post_save
from django.dispatch import receiver
from icecream import ic

from .models import Attendance
from ..groups.lesson_date_calculator import calculate_lessons
from ...finances.compensation.models import Bonus
from ...finances.finance.models import Finance, Kind, SaleStudent
from ...notifications.models import Notification


@receiver(post_save, sender=Attendance)
def on_attendance_create(sender, instance: Attendance, created, **kwargs):


    if instance.lid:

        attendances_count = Attendance.objects.filter(lid=instance.lid).count()

        if attendances_count == 1:
            if instance.reason == "IS_PRESENT":
                instance.lid.is_student = True
                instance.lid.save()

            else:
                instance.lid.is_student = True
                instance.lid.save()
                stage_name = f"{attendances_count} darsga qatnashmagan"
                Notification.objects.create(
                    user=instance.lid.call_operator,
                    comment=f"Lead {instance.lid.first_name} {instance.lid.phone_number} - {stage_name} !",
                    come_from=instance.lid,
                )

    if instance.student:
        attendances_count = Attendance.objects.filter(student=instance.student).count()

        if attendances_count == 1:
            if instance.reason in ["UNREASONED","REASONED"]:
                instance.student.new_student_stages = "BIRINCHI_DARSGA_KELMAGAN"
                instance.student.save()

            if instance.reason == "IS_PRESENT":
                instance.student.new_student_stages = "BIRINCHI_DARS"
                instance.student.save()

        if attendances_count > 1 and instance.reason == "IS_PRESENT":

            if instance.student.balance_status =="INACTIVE":
                Notification.objects.create(
                    user=instance.student.sales_manager,
                    comment=f"Talaba {instance.student.first_name} {instance.student.phone} - "
                            f"{attendances_count} darsga qatnashdi va balansi statusi inactive, To'lov haqida ogohlantiring!",
                    come_from=instance.lid,
                )

        if attendances_count > 1 and instance.reason == "UNREASONED":

            Notification.objects.create(
                user=instance.student.sales_manager,
                comment=f"Talaba {instance.student.first_name} {instance.student.phone} - {attendances_count} darsga qatnashmagan!",
                come_from=instance.student,
            )



@receiver(post_save, sender=Attendance)
def on_attendance_money_back(sender, instance: Attendance, created, **kwargs):
    if not created or not instance.student or not instance.group:
        return

    if instance.reason not in ["IS_PRESENT", "UNREASONED", "REASONED"]:
        return

    kind = Kind.objects.get(name="Lesson payment")
    is_first_income = Finance.objects.filter(action="INCOME").count() == 0

    # Get teacher bonus as Decimal (if exists)
    teacher_bonus = Bonus.objects.filter(
        user=instance.group.teacher,
        name="O’quvchi to’lagan summadan foiz beriladi"
    ).values("amount").first()

    bonus_percent = Decimal(teacher_bonus["amount"]) if teacher_bonus else Decimal("0.0")

    price = Decimal(instance.group.price)


    if instance.group.price_type == "DAILY":

        # Get user sale if there is any...
        if instance.student is not None:
            sale = SaleStudent.objects.filter(
                student = instance.student,
            ).first()
        else:
            sale = SaleStudent.objects.filter(
                lid=instance.lid,
            ).first()

        # DAILY PAYMENT TYPE
        if sale:
            ic(sale.amount)
            ic(price * (sale.amount / 100))
            price = price - price * (sale.amount / 100)
            ic(price)
        bonus_amount = price * bonus_percent / Decimal("100")
        income_amount = price - bonus_amount

        instance.amount = instance.group.price
        instance.save()

        ic(income_amount , bonus_amount)

        # # Teacher bonus (EXPENSE)
        # Finance.objects.create(
        #     action="EXPENSE",
        #     amount=bonus_amount,
        #     kind=kind,
        #     attendance=instance,
        #     student=instance.student,
        #     stuff=instance.group.teacher,
        #     is_first=is_first_income,
        #     comment=f"Talaba {instance.student.first_name} {instance.student.last_name} dan {instance.created_at.strftime('%d-%m-%Y %H:%M')}"
        # )
        instance.group.teacher.balance += float(bonus_amount)
        instance.group.teacher.save()

        # Center's income
        Finance.objects.create(
            action="INCOME",
            amount=income_amount,
            kind=kind,
            attendance=instance,
            student=instance.student,
            is_first=is_first_income,
            comment=f"Talaba {instance.student.first_name} {instance.student.last_name} dan {instance.created_at.strftime('%d-%m-%Y %H:%M')}"
        )

        instance.student.balance -= float(price)
        instance.student.save()

    elif instance.group.price_type == "MONTHLY":

        # MONTHLY PAYMENT TYPE
        current_month = datetime.date.today().replace(day=1)
        month_key = current_month.strftime("%Y-%m")

        lesson_days_qs = instance.group.scheduled_day_type.all()
        lesson_days = ",".join([day.name for day in lesson_days_qs]) if lesson_days_qs else ""

        holidays = []
        days_off = ["Yakshanba"]

        lessons_per_month = calculate_lessons(
            start_date=current_month.strftime("%Y-%m-%d"),
            end_date=instance.group.finish_date.strftime("%Y-%m-%d"),
            lesson_type=lesson_days,
            holidays=holidays,
            days_off=days_off,
        )

        lessons = lessons_per_month.get(month_key, [])
        lesson_count = len(lessons)
        ic(lesson_count)

        if lesson_count > 0:

            # Get user sale if there is any...
            if instance.student is not None:
                sale = SaleStudent.objects.filter(
                    student=instance.student,
                    # expire_date__lte=datetime.datetime.now(),
                ).first()
            else:
                sale = SaleStudent.objects.filter(
                    lid=instance.lid,
                    # expire_date__lte=datetime.datetime.now(),
                ).first()

                # DAILY PAYMENT TYPE
            per_lesson_price = price / lesson_count
            if sale:
                ic(sale.amount)
                ic(per_lesson_price * (sale.amount / 100))
                per_lesson_price = per_lesson_price - per_lesson_price * (sale.amount / 100)
                ic(per_lesson_price)

            instance.amount = per_lesson_price
            instance.save()

            bonus_amount = per_lesson_price * bonus_percent / Decimal("100")
            income_amount = per_lesson_price - bonus_amount

            ic(per_lesson_price, bonus_amount, income_amount)

            # Update balances
            instance.student.balance -= float(per_lesson_price)
            instance.student.save()



            # Finance.objects.create(
            #     action="EXPENSE",
            #     amount=bonus_amount,
            #     kind=kind,
            #     attendance=instance,
            #     student=instance.student,
            #     stuff=instance.group.teacher,
            #     is_first=is_first_income,
            #     comment=f"Talaba {instance.student.first_name} {instance.student.last_name} dan {instance.created_at.strftime('%d-%m-%Y %H:%M' )}"
            # )
            instance.group.teacher.balance += float(bonus_amount)
            instance.group.teacher.save()

            Finance.objects.create(
                action="INCOME",
                amount=income_amount,
                kind=kind,
                attendance=instance,
                student=instance.student,
                is_first=is_first_income,
                comment=f"Talaba {instance.student.first_name} dan {instance.created_at.strftime('%d-%m-%Y %H:%M')}"
            )
        else:
            print(f"No lessons scheduled for {month_key}, skipping balance deduction.")
