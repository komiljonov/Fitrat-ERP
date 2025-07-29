from data.department.filial.models import Filial
from django.db.models.signals import m2m_changed, post_save
from django.dispatch import receiver

from data.account.models import CustomUser
from data.command.models import UserFilial
from data.finances.timetracker.sinx import TimetrackerSinc


# Handle additions and removals
@receiver(m2m_changed, sender=CustomUser.filial.through)
def sync_user_filials(sender, instance: CustomUser, action, pk_set, **kwargs):
    if action == 'post_add':
        for filial_id in pk_set:
            filial = Filial.objects.get(pk=filial_id)
            UserFilial.objects.get_or_create(user=instance, filial=filial)

    elif action == 'post_remove':
        UserFilial.objects.filter(user=instance, filial_id__in=pk_set).update(is_archived=True)


@receiver(post_save, sender=CustomUser)
def create_user_filials_on_create(sender, instance: CustomUser, created, **kwargs):
    if created:
        for filial in instance.filial.all():
            UserFilial.objects.get_or_create(user=instance, filial=filial)


@receiver(post_save, sender=Filial)
def create_user_filials_on_save(sender, instance: Filial, created, **kwargs):
    if created:
        tt = TimetrackerSinc()
        data = {
            "name": instance.name,
        }
        response = tt.create_filial(data)

        print(response)

        id = response.get("id")
        instance.tt_filial = id
        instance.save()
        print(response)
