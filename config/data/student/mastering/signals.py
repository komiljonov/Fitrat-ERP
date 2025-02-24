from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.context_processors import request

from .models import MasteringTeachers
from ..attendance.models import Attendance
from ...account.models import CustomUser
from ...finances.compensation.models import Bonus
from ...finances.finance.models import KpiFinance, Finance
from ...lid.new_lid.models import Lid
from ...notifications.models import Notification


@receiver(post_save, sender=MasteringTeachers)
def on_create(sender, instance: MasteringTeachers, created, **kwargs):
    if created:
        user = CustomUser.objects.filter(id=instance.teacher.id, role="TEACHER").first()
        if user:
            user.ball += instance.ball
            user.save()
            Notification.objects.create(
                user=user,
                comment=f"Sizning darajangiz {instance.ball} ball oshirildi ! ",
                come_from=instance
            )

#------------- Monitoring edits -----------#


#        Call Operator

# Markazga kelgan oq’uvchi uchun bonus #
@receiver(post_save, sender=Attendance)
def bonus_call_operator(sender, instance: Attendance, created, **kwargs):
    if created:
        attendances_count = Attendance.objects.filter(student=instance.student,reason="IS_PRESENT").count()
        if attendances_count == 1:
            bonus = Bonus.objects.filter(user=instance.student.call_operator, name="Markazga kelgan oq’uvchi uchun bonus").first()
            if bonus:

                KpiFinance.objects.create(
                    user=instance.student.call_operator,
                    reason="Markazga kelgan oq’uvchi uchun bonus",
                    amount=bonus.amount,
                    type="INCOME",
                    lid=instance.lid,
                )



#Sotuv menejeri

# Yaratilgan buyurtma uchun bonus #   ✅
@receiver(post_save, sender=Lid)
def new_created_order(sender, instance: Lid, created, **kwargs):
    if not created:

        bonus = Bonus.objects.filter(user=instance.student.call_operator,
                                     name="Markazga kelgan oq’uvchi uchun bonus").first()

        is_bonused = KpiFinance.objects.filter(
            lid=instance,
        ).count()

        if (instance.lid_stage_type == "ORDERED_LID" and instance.filial is not
                None and is_bonused == 0 and instance.sales_manager):
            KpiFinance.objects.create(
                user=instance.sales_manager,
                lid=instance,
                student=None,
                reason=f"{instance.first_name} {instance.last_name} ning markazga kelganligi uchun bonus !",
                amount=bonus.amount,
                type="INCOME",
            )

@receiver(post_save, sender=Attendance)
def new_created_order(sender, instance: Attendance, created, **kwargs):
    if created:
        attendances_count = Attendance.objects.filter(student=instance.student,reason="IS_PRESENT").count()
        amount = Bonus.objects.filter(user=instance.student.sales_manager, name="Sinov darsiga kelgani uchun bonus #")
        if attendances_count == 1:
            KpiFinance.objects.create(
                user=instance.student.sales_manager,
                student=instance.student,
                reason=f"{instance.student.first_name} {instance.student.last_name} ning birinchi darsga kelganligi uchun!",
                amount=amount.amount,
            )
#Sinov darsiga kelgani uchun bonus #
@receiver(post_save, sender=Finance)
def new_created_order(sender, instance: Finance, created, **kwargs):
    if created and instance.student:
        count = Finance.objects.filter(student=instance.student,
                                       action="INCOME",
                                       ).all()
        amount = Bonus.objects.filter(user=instance.student.sales_manager,
                                      name="Sinov darsiga kelgani uchun bonus #")

        if count == 1:
            KpiFinance.objects.create(
                user=instance.student.sales_manager,
                student=instance.student,
                amount=amount.amount,
                type="INCOME",
                reason=f"{instance.student.first_name} {instance.student.last_name} ning active o'quvchiga o'tganligi uchun bonus ",
            )

#jarima : Sinov darsiga yozilb kemaganlar uchun jarima #

@receiver(post_save, sender=Attendance)
def new_created_order(sender, instance: Attendance, created, **kwargs):
    if created:
        attendances_count = Attendance.objects.filter(lid=instance.lid,reason=["UNREASONED"]).count()
        amount = Bonus.objects.filter(user=instance.lid.sales_manager,
                                      name="Sinov darsiga yozilb kemaganlar uchun jarima #")
        if attendances_count == 1:
            KpiFinance.objects.create(
                user=instance.lid.sales_manager,
                student=instance.lid,
                amount=amount.amount,
                type="EXPENSE",
                reason=f"{instance.lid.first_name} {instance.lid.last_name} ning birinchi darsga kelmaganligi uchun jarima "
            )



