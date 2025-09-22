from django.dispatch import receiver
from django.utils import timezone

from django.db.models.signals import pre_save, post_save

from data.firstlesson.models import FirstLesson
from data.student.studentgroup.models import StudentGroup


@receiver(post_save, sender=FirstLesson)
def on_new_first_lesson(sender, instance: "FirstLesson", created, **kwargs):
    if not created:
        return  # only run on creation

    instance.lead.ordered_stages = "BIRINCHI_DARS_BELGILANGAN"
    instance.lead.save(update_fields=["ordered_stages"])

    if (
        instance.lead.sales_manager
        and instance.lead.sales_manager.f_sm_bonus_create_first_lesson > 0
    ):
        instance.lead.call_operator.transactions.create(
            reason="BONUS",
            lead=instance.lead,
            first_lesson=instance,
            amount=instance.lead.sales_manager.f_sm_bonus_create_first_lesson,
            comment=f"Yangi sinov darsi uchun bonus. Buyurtma: {instance.lead.first_name} {instance.lead.last_name}. Sinov darsi: {instance.id}",
        )


@receiver(pre_save, sender=FirstLesson)
def on_update(sender, instance: "FirstLesson", **kwargs):
    # Only handle updates
    if instance._state.adding:
        return

    # No-op unless group actually changed
    changes = set(instance.changed_fields() or [])
    if "group" not in changes:
        return

    # Fetch previous group_id for this FirstLesson
    try:
        old = sender.objects.only("group_id").get(pk=instance.pk)
    except sender.DoesNotExist:
        return

    old_gid = old.group_id
    new_gid = instance.group_id
    if old_gid == new_gid:
        return

    # 1) Archive old group's StudentGroup (active rows) for this lead
    StudentGroup.objects.filter(
        lid_id=instance.lead_id,
        group_id=old_gid,
        is_archived=False,
    ).update(is_archived=True, archived_at=timezone.now())

    # 2) Create or unarchive the new group's StudentGroup for this lead
    sg, created = StudentGroup.objects.update_or_create(
        lid_id=instance.lead_id,
        group_id=new_gid,
        defaults=dict(first_lesson=instance, is_archived=False),
    )
    if not created and sg.is_archived:
        sg.is_archived = False
        sg.archived_at = None
        sg.first_lesson = instance
        sg.save(update_fields=["is_archived", "archived_at", "first_lesson"])
