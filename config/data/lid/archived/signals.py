from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Archived, Frozen
from ..new_lid.models import Lid
from ...comments.models import Comment
from ...logs.models import Log
from ...notifications.models import Notification
from ...student.studentgroup.models import StudentGroup


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

            sg = StudentGroup.objects.filter(student=instance.student).all()
            for ssg in sg:
                ssg.is_archived = True
                ssg.save()

                Notification.objects.create(
                    user=instance.student.user,
                    choice="Archive",
                    comment=f"Siz {ssg.group.name} guruhidan {instance.created_at.date()} sanasida {instance.reason} sababi bilan arxivlandingiz!",
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
            model_action="Archived",
            lid=instance.lid,
            student=instance.student,
            archive=instance,
            comment=f"Arxivlandi {instance.created_at.date()} sanasida, sabab : {instance.comment.comment if instance.comment else ""}",
        )

    if not created and instance.is_archived == False:
        Log.objects.create(
            app="Archive",
            model="Unarchived",
            action="Log",
            model_action="Updated",
            lid=instance.lid,
            student=instance.student,
            archive=instance,
            comment=f"Arxivdan chiqarildi {instance.updated_at.date()} sanasida, sabab : {instance.comment.comment if instance.comment else ""}",
        )