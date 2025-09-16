from django.dispatch import receiver

from django.db.models.signals import post_save

from data.firstlesson.models import FirstLesson


@receiver(post_save, sender=FirstLesson)
def on_new_first_lesson(sender, instance: "FirstLesson", created, **kwargs):
    if not created:
        return  # only run on creation

    instance.lead.ordered_stages = "BIRINCHI_DARS_BELGILANGAN"
    instance.lead.save(update_fields=["ordered_stages"])


# @receiver(post_save, sender=FirstLesson)
# def on_new_first_lesson(sender, instance: "FirstLesson", created, **kwargs):

#     if not created:
#         return

#     instance.group.students.get_or_create(lid=instance.lead, first_lesson=instance)
