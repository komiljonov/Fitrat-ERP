from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver

from data.archive.models import Archive
from data.comments.models import Comment


@receiver(pre_save, sender=Archive)
def on_create(sender, instance: Archive, created, **kwargs):

    if not created or instance.lead is None:
        return

    comment = Comment.objects.create(
        creator=instance.creator,
        lid=instance.lead,
        student=instance.student,
        comment=f"Arxivlandi {instance.created_at.date()} sanasida, sabab: {instance.reason}",
    )

    instance.comment = comment
