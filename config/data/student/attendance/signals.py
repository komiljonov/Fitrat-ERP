import calendar
import datetime
from decimal import Decimal

from django.db.models.signals import post_save
from django.dispatch import receiver
from icecream import ic

from .models import Attendance
from ..groups.lesson_date_calculator import calculate_lessons
from ..homeworks.models import Homework_history, Homework
from ..student.models import Student
from ..subject.models import Theme
from ...finances.compensation.models import Bonus
from ...finances.finance.models import Finance, Kind, SaleStudent
from ...lid.new_lid.models import Lid
from ...notifications.models import Notification

from threading import local

_signal_state = local()


def get_sale_for_instance(instance):
    if instance.student:
        return SaleStudent.objects.filter(student=instance.student).select_related("sale").first()
    return SaleStudent.objects.filter(lid=instance.lid).select_related("sale").first()


def apply_discount(price, sale):
    if sale and sale.sale and sale.sale.amount:
        try:
            sale_percent = Decimal(sale.sale.amount)
            ic("sales_percent", sale_percent)

            discount = price * sale_percent / Decimal("100")
            ic("Discount:", discount)
            return price - discount
        except (TypeError, ValueError, Decimal.InvalidOperation):
            ic("Invalid sale amount")
    return price


def calculate_bonus_and_income(price, bonus_percent):
    bonus_amount = price * bonus_percent / Decimal("100")
    income_amount = price - bonus_amount

    ic("Bonus:", bonus_amount, "income:", income_amount)
    return bonus_amount, income_amount


def create_finance_record(action, amount, kind, instance, student, teacher=None, is_first=False):
    return Finance.objects.create(
        action=action,
        amount=amount,
        kind=kind,
        attendance=instance,
        student=student,
        stuff=teacher,
        is_first=is_first,
        comment=f"Talaba {student.first_name} {student.last_name} dan {instance.created_at.strftime('%d-%m-%Y %H:%M')}"
    )


@receiver(post_save, sender=Attendance)
def on_attendance_create(sender, instance: Attendance, created, **kwargs):
    if instance.lid:
        attendances_count = Attendance.objects.filter(lid=instance.lid).count()

        if attendances_count == 1 and instance.reason != "IS_PRESENT":
            Notification.objects.create(
                user=instance.lid.call_operator,
                comment=f"Lead {instance.lid.first_name} {instance.lid.phone_number} - {attendances_count} darsga qatnashmagan !",
                come_from=instance.lid,
            )

        instance.lid.is_student = True
        instance.lid.save()

        student = Lid.objects.filter(id=instance.lid.id).first()
        if student:
            student = Student.objects.filter(id=student.student.id).first()
            if student:
                student.new_student_stages="BIRINCHI_DARSGA_KELMAGAN"
                student.save()

    if instance.student:
        attendances_count = Attendance.objects.filter(student=instance.student).count()

        if attendances_count == 1:
            stage = "BIRINCHI_DARS" if instance.reason == "IS_PRESENT" else "BIRINCHI_DARSGA_KELMAGAN"
            instance.student.new_student_stages = stage
            instance.student.save()

        if attendances_count > 1:
            if instance.reason == "IS_PRESENT" and instance.student.balance_status == "INACTIVE":
                Notification.objects.create(
                    user=instance.student.sales_manager,
                    comment=f"Talaba {instance.student.first_name} {instance.student.phone} - {attendances_count} darsga qatnashdi va balansi statusi inactive, To'lov haqida ogohlantiring!",
                    come_from=instance.lid,
                )
            elif instance.reason == "UNREASONED":
                Notification.objects.create(
                    user=instance.student.sales_manager,
                    comment=f"Talaba {instance.student.first_name} {instance.student.phone} - {attendances_count} darsga qatnashmagan!",
                    come_from=instance.student,
                )


@receiver(post_save, sender=Attendance)
def on_attendance_money_back(sender, instance: Attendance, created, **kwargs):
    if getattr(_signal_state, "processing", False):
        return

    _signal_state.processing = True
    try:
        if not created or not instance.student or not instance.group:
            return

        if instance.reason not in ["IS_PRESENT", "UNREASONED", "REASONED"]:
            return

        kind = Kind.objects.get(name="Lesson payment")
        is_first_income = not Finance.objects.filter(action="INCOME").exists()

        bonus = Bonus.objects.filter(
            user=instance.group.teacher,
            name="O’quvchi to’lagan summadan foiz beriladi"
        ).values("amount").first()

        bonus_percent = Decimal(bonus["amount"]) if bonus else Decimal("0.0")

        price = Decimal(instance.group.price)
        sale = get_sale_for_instance(instance)

        if instance.group.price_type == "DAILY":
            final_price = apply_discount(price, sale)

            ic("Before save - balance:", instance.student.balance)
            instance.amount = final_price
            instance.save(update_fields=["amount"])

            instance.student.balance -= final_price
            instance.student.save(update_fields=["balance"])
            ic("After save - balance:", instance.student.balance)

            bonus_amount, income_amount = calculate_bonus_and_income(final_price, bonus_percent)

            instance.group.teacher.balance += bonus_amount
            instance.group.teacher.save(update_fields=["balance"])

            create_finance_record(
                "EXPENSE",
                income_amount,
                kind,
                instance,
                instance.student,
                is_first=is_first_income
            )

        elif instance.group.price_type == "MONTHLY":
            current_month = datetime.date.today().replace(day=1)
            month_key = current_month.strftime("%Y-%m")
            last_day = calendar.monthrange(current_month.year, current_month.month)[1]
            end_of_month = current_month.replace(day=last_day)

            ic(month_key, end_of_month)

            lesson_days_qs = instance.group.scheduled_day_type.all()
            lesson_days = ",".join([day.name for day in lesson_days_qs]) if lesson_days_qs else ""

            holidays = []
            days_off = ["Yakshanba"]

            lessons_per_month = calculate_lessons(
                start_date=current_month.strftime("%Y-%m-%d"),
                end_date=end_of_month.strftime("%Y-%m-%d"),
                lesson_type=lesson_days,
                holidays=holidays,
                days_off=days_off,
            )

            lessons = lessons_per_month.get(month_key, [])
            lesson_count = len(lessons)

            ic("lesson_count", lesson_count)

            if lesson_count > 0:
                per_lesson_price = price / lesson_count
                per_lesson_price = apply_discount(per_lesson_price, sale)


                ic("MINUS FROM STUDENT BALANCE:", per_lesson_price)
                instance.student.balance -= per_lesson_price
                instance.student.save(update_fields=["balance"])

                instance.amount = per_lesson_price
                instance.save(update_fields=["amount"])



                bonus_amount, income_amount = calculate_bonus_and_income(per_lesson_price, bonus_percent)

                instance.group.teacher.balance += bonus_amount
                instance.group.teacher.save(update_fields=["balance"])

                create_finance_record(
                    "EXPENSE",
                    income_amount,
                    kind,
                    instance,
                    instance.student,
                    is_first=is_first_income
                )

            else:
                ic(f"No lessons scheduled for {month_key}, skipping balance deduction.")

    finally:
        _signal_state.processing = False


@receiver(post_save, sender=Attendance)
def on_group_days_update(sender, instance, created, **kwargs):
    if created:
        group_first_att = Attendance.objects.filter(group=instance.group).count()
        if group_first_att == 1:
            total_lessons = Theme.objects.filter(course=instance.group.course).count()

            week_days = [days.name for days in instance.scheduled_day_type.all()]

            finish_date = datetime.today() + datetime.timedelta(days=365)

            lesson_dates = calculate_lessons(
                start_date=instance.start_date,
                end_date=finish_date,
                lesson_type=str(week_days),
                holidays=[""],
                days_off=["Yakshanba"]
            )
            print(lesson_dates)
            if len(lesson_dates) >= total_lessons:
                actual_end_date = lesson_dates[total_lessons - 1]
                ic(actual_end_date)

                instance.group.finish_date = actual_end_date
                instance.group.save()

            else:
                if lesson_dates:
                    instance.group.finish_date = lesson_dates[-1]
                    instance.group.save()



# @receiver(post_save, sender=Attendance)
# def on_mastering_update(sender, instance : Attendance, created, **kwargs):
#     if created and instance.student:
#         print(instance.theme.all())
#         first_theme = instance.theme.first()
#         if first_theme:
#             themes = Theme.objects.filter(id=first_theme.id)
#         else:
#             themes = Theme.objects.none()
#         print(themes)
#         homework = Homework.objects.filter(theme=themes).first()
#         print("----")
#         if homework:
#             Homework_history.objects.filter(
#                 homework=homework,
#                 group=instance.group,
#                 student=instance.student,
#                 mark=0
#             )

