from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Student, Archived
from ...comments.models import Comment
from ...notifications.models import Notification


@receiver(post_save, sender=Archived)
def on_create(sender, instance: Archived, created, **kwargs):
    if created:
        if instance.student:
            instance.student.is_archived = True
            instance.student.save()

            comment = Comment.objects.create(
                creator=instance.creator,
                student=instance.student,
                lid=None,
                comment=f"Arxivlandi {instance.created_at} sanasida, sabab: {instance.reason}",
            )

        if instance.lid:
            instance.lid.is_archived = True
            instance.lid.save()
            comment = Comment.objects.create(
                creator=instance.creator,
                lid=instance.lid,
                student=None,
                comment=f"Arxivlandi {instance.created_at} sanasida, sabab: {instance.reason}",
            )


