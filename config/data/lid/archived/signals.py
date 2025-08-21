from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Archived, Frozen
from ..new_lid.models import Lid
from ...comments.models import Comment
from ...logs.models import Log


@receiver(post_save, sender=Archived)
def on_create(sender, instance: Archived, created, **kwargs):
    if created and instance.is_archived == True:
        if instance.student:
            instance.student.is_archived = True
            instance.student.save()

            date = instance.created_at.date()

            comment = Comment.objects.create(
                creator=instance.creator,
                student=instance.student,
                lid=None,
                comment=f"Arxivlandi {date} sanasida, sabab: {instance.reason}",
            )

        if instance.lid:
            instance.lid.is_archived = True
            instance.lid.save()
            comment = Comment.objects.create(
                creator=instance.creator,
                lid=instance.lid,
                student=None,
                comment=f"Arxivlandi {instance.created_at.date()} sanasida, sabab: {instance.reason}",
            )
    if not created and instance.is_archived == False:
        if instance.student:
            instance.student.is_archived = False
            instance.student.save()

            date = instance.created_at.date()

            comment = Comment.objects.create(
                creator=instance.creator,
                student=instance.student,
                lid=None,
                comment=f"Arxivdan chiqarildi {date} sanasida, sabab: {instance.reason}",
            )
        if instance.lid:
            instance.lid.is_archived = False
            instance.lid.save()
            comment = Comment.objects.create(
                creator=instance.creator,
                lid=instance.lid,
                student=None,
                comment=f"Arxivlandi {instance.created_at.date()} sanasida, sabab: {instance.reason}",
            )


@receiver(post_save, sender=Frozen)
def on_create(sender, instance: Frozen, created, **kwargs):
    if created and instance.is_frozen == True:
        if instance.student:
            instance.student.is_frozen = True
            instance.student.save()

        if instance.lid:
            instance.lid.is_frozen = True
            instance.lid.save()

    if not created and instance.is_frozen == False:
        if instance.student:
            instance.student.is_frozen = False
            instance.student.save()

        if instance.lid:
            instance.lid.is_frozen = False
            instance.lid.save()


@receiver(post_save, sender=Archived)
def on_create(sender, instance: Archived, created, **kwargs):
    if created and instance.is_archived == True:

        Log.objects.create(
            app="Archive",
            model="Archived",
            action="Log",
            model_action="Created",
            lid=instance.lid,
            student=instance.student,
            archive=instance,
            comment=instance.comment.comment if instance.comment else None,
        )

    if not created and instance.is_archived == False:
        Log.objects.create(
            app="Archive",
            model="Archived",
            action="Log",
            model_action="Updated",
            lid=instance.lid,
            student=instance.student,
            archive=instance,
            comment=instance.comment.comment if instance.comment else None,
        )