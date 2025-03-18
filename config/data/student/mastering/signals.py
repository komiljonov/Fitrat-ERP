from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.context_processors import request
from icecream import ic

from .models import MasteringTeachers
from ..attendance.models import Attendance
from ..lesson.models import FirstLLesson
from ..student.models import Student
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
@receiver(post_save, sender=FirstLLesson)
def bonus_call_operator(sender, instance: FirstLLesson, created, **kwargs):
    if not created:
        if instance.lid.lid_stage_type == "ORDERED_LID":
            ic("-----------")
            bonus = Bonus.objects.filter(user=instance.lid.call_operator,
                                         name="Markazga kelgan oq’uvchi uchun bonus").first()
            ic(bonus)
            if bonus and instance.lid.call_operator:
                KpiFinance.objects.create(
                    user=instance.lid.call_operator,
                    reason="Markazga kelgan oq’uvchi uchun bonus",
                    amount=bonus.amount if bonus.amount else 0,
                    type="INCOME",
                    lid=instance,
                    student=None
                )


#Sotuv menejeri

# Yaratilgan buyurtma uchun bonus #   ✅
@receiver(post_save, sender=Lid)
def new_created_order(sender, instance: Lid, created, **kwargs):
    if not created:

        bonus = Bonus.objects.filter(user=instance.call_operator,
                                     name="Yaratilgan buyurtma uchun bonus").first()

        is_bonused = KpiFinance.objects.filter(
            lid=instance,
        ).count()
        ic(bonus,is_bonused)

        if (instance.lid_stage_type == "ORDERED_LID" and instance.filial is not
                None and is_bonused == 0 and instance.sales_manager):
            KpiFinance.objects.create(
                user=instance.sales_manager,
                lid=instance,
                student=None,
                reason=f"{instance.first_name} {instance.last_name} "
                       f"ning buyurtma sifatifa yaratilganligi uchun bonus !",
                amount=bonus.amount if bonus else 0,
                type="INCOME",
            )




@receiver(post_save, sender=Attendance)
def new_created_order(sender, instance: Attendance, created, **kwargs):
    if created:
        attendances_count = Attendance.objects.filter(student=instance.student,reason="IS_PRESENT").count()
        amount = Bonus.objects.filter(user=instance.student.sales_manager,
                                      name="Sinov darsiga kelgani uchun bonus ")
        if attendances_count == 1 and instance.student.sales_manager:
            KpiFinance.objects.create(
                lid=None,
                user=instance.student.sales_manager,
                student=instance.student,
                reason=f"{instance.student.first_name} {instance.student.last_name} ning birinchi darsga kelganligi uchun!",
                amount=amount.amount if amount.amount else 0,
                type="INCOME",
            )



#Sinov darsiga kelgani uchun bonus #
@receiver(post_save, sender=Finance)
def new_created_order(sender, instance: Finance, created, **kwargs):
    if created and instance.student:
        count = Finance.objects.filter(student=instance.student,
                                       action="INCOME",
                                       ).count()
        amount = Bonus.objects.filter(user=instance.student.sales_manager,
                                      name="Aktiv o'quvchiga aylangan yangi o’quvchi uchun bonus ")

        if count == 1 and instance.student.balance_status=="ACTIVE" and instance.student.sales_manager:
            KpiFinance.objects.create(
                user=instance.student.sales_manager,
                student=instance.student,
                amount=amount.amount if amount.amount else 0,
                type="INCOME",
                reason=f"{instance.student.first_name} {instance.student.last_name} ning active o'quvchiga o'tganligi uchun bonus ",
            )



#jarima : Sinov darsiga yozilb kemaganlar uchun jarima #
@receiver(post_save, sender=Attendance)
def new_created_order(sender, instance: Attendance, created, **kwargs):
    if created:
        attendances_count = Attendance.objects.filter(student=instance.student,reason=["UNREASONED"]).count()
        amount = Bonus.objects.filter(user=instance.student.sales_manager,
                                      name="Sinov darsiga yozilb kemaganlar uchun jarima (Jarima)")
        if attendances_count == 1 and instance.student.sales_manager:
            KpiFinance.objects.create(
                user=instance.student.sales_manager,
                student=instance.student,
                amount=amount.amount if amount.amount else 0,
                type="EXPENSE",
                reason=f"{instance.student.first_name} {instance.student.last_name}"
                       f" ning birinchi darsga kelmaganligi uchun jarima "
            )



#Serveis menejeri  -   Hizmat ko’rsatgan har bir active o’quvchi uchun bonus #
@receiver(post_save, sender=Student)
def new_created_order(sender, instance: Student, created, **kwargs):
    if not created:
        finance = Finance.objects.filter(student=instance,action="INCOME").count()
        if instance.service_manager and instance.balance_status == "ACTIVE" and finance == 1:
            amount = Bonus.objects.filter(user=instance.service_manager,
                                          name="Hizmat ko’rsatgan har bir Aktiv o'quvchi uchun bonus ")
            KpiFinance.objects.create(
                user=instance.service_manager,
                student=instance,
                amount=amount.amount if amount else 0,
                type="INCOME",
                reason=f"Hizmat ko'rsatgan {instance.first_name} {instance.last_name} o'quvchi uchun bonus ",
            )



#Agar o’quvchi ketib qolsa jarima yoziladi (Jarima)
@receiver(post_save, sender=Student)
def new_created_order(sender, instance: Student, created, **kwargs):
    if not created and instance.is_archived == True:
        att = Attendance.objects.filter(student=instance,reason="UNREASONED").count()
        if att > 2 and instance.service_manager:
            amount = Bonus.objects.filter(user=instance.service_manager,
                                          name="Agar o’quvchi ketib qolsa jarima yoziladi (Jarima)")
            KpiFinance.objects.create(
                user=instance.service_manager,
                student=instance,
                amount=amount.amount if amount.amount else 0,
                type="EXPENSE",
                reason=f"{instance.first_name} {instance.last_name} ning o'quv jarayonini tuxtatganligi uchun jarima!"
            )











