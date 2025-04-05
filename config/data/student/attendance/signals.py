import datetime
from decimal import Decimal

from django.db.models.signals import post_save
from django.dispatch import receiver
from icecream import ic

from .models import Attendance
from ..groups.lesson_date_calculator import calculate_lessons
from ...finances.compensation.models import Bonus
from ...finances.finance.models import Finance, Kind
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
    if created:
        if instance.reason in ["IS_PRESENT", "UNREASONED", "REASONED"] and instance.group:
            if instance.group.price_type == "DAILY":
                if instance.student:

                    is_first = True if Finance.objects.filter(action="INCOME").count() == 1 else False
                    kind = Kind.objects.get(name="Lesson payment")

                    teacher_bonus = Bonus.objects.filter(
                        user=instance.group.teacher,
                        name="O’quvchi to’lagan summadan foiz beriladi"
                    ).values("amount").first()
                    ic(teacher_bonus)

                    bonus = teacher_bonus.get("amount") if teacher_bonus else 0
                    ic(bonus)
                    if teacher_bonus:
                        ic(bonus)
                        Finance.objects.create(
                            action="EXPENSE",
                            amount=instance.group.price * (float(bonus) / float("100")),
                            kind=kind,
                            attendance=instance,
                            student=instance.student,
                            is_first=is_first,
                            comment=f"Talaba {instance.student.first_name} dan {instance.created_at}"
                        )
                        instance.group.teacher.balance += instance.group.price * (float(bonus) / float("100"))
                        instance.group.teacher.save()


                        Finance.objects.create(
                            action="INCOME",
                            amount=instance.group.price * (float("1") - float(bonus) / float("100")),
                            kind=kind,
                            attendance=instance,
                            student=instance.student,
                            is_first=is_first,
                            comment=f"Talaba {instance.student.first_name} dan {instance.created_at}"
                        )
                        instance.student.balance -= instance.group.price
                        instance.student.save()
                else:
                    print("Attendance does not have a related student.")

            elif instance.group.price_type == "MONTHLY":
                if instance.student:
                    # Get the first day of the current month (YYYY-MM format)
                    current_month_start = datetime.date.today().replace(day=1).strftime("%Y-%m-%d")

                    # Extract lesson days from group and format as a comma-separated string
                    lesson_days_queryset = instance.group.scheduled_day_type.all()  # Ensure `.all()` is used
                    lesson_days = ",".join([day.name for day in lesson_days_queryset]) if lesson_days_queryset else ""

                    # Define holidays & days off
                    holidays = []
                    days_off = ["Yakshanba"]

                    # Calculate lessons for the month from the start of the month
                    lessons_per_month = calculate_lessons(
                        start_date=current_month_start,  # Always start from the 1st of the month
                        end_date=instance.group.finish_date.strftime("%Y-%m-%d"),
                        lesson_type=lesson_days,
                        holidays=holidays,
                        days_off=days_off,
                    )

                    ic(lessons_per_month.get(current_month_start[:7], []))
                    lesson_count = len(lessons_per_month.get(current_month_start[:7], []))  # Extract YYYY-MM

                    ic(lesson_count)

                    if lesson_count > 0:
                        price_per_lesson = instance.group.price / lesson_count
                        ic(price_per_lesson)
                        instance.student.balance -= price_per_lesson
                        instance.student.save()

                        teacher_bonus = Bonus.objects.filter(user=instance.group.teacher,
                                                             name="O’quvchi to’lagan summadan foiz beriladi")
                        if teacher_bonus:
                            bonus = teacher_bonus.get("amount")

                            instance.group.teacher.balance += price_per_lesson * (bonus / 100)
                            kind = Kind.objects.get(name="Lesson payment")
                            is_first = True if Finance.objects.filter(action="INCOME").count() == 1 else False
                            Finance.objects.create(
                                action="INCOME",
                                amount=instance.group.price * (float("1") - float(bonus) / float("100")),
                                kind=kind,
                                attendance=instance,
                                student=instance.student,
                                is_first=is_first,
                                comment=f"Talaba {instance.student.first_name} dan {instance.created_at}"
                            )

                    else:
                        print(f"No lessons scheduled for {current_month_start}, skipping balance deduction.")

