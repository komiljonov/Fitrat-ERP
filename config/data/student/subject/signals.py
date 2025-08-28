from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import timedelta
from .models import Theme
from data.student.groups.models import Group

UZBEK_WEEKDAYS = [
    "Dushanba",
    "Seshanba",
    "Chorshanba",
    "Payshanba",
    "Juma",
    "Shanba",
    "Yakshanba",
]


def get_next_valid_day(current_date, valid_day_numbers):
    """
    Find the next date after `current_date` that matches one of the valid weekday numbers.
    """
    for i in range(1, 8):  # Max one week forward
        next_day = current_date + timedelta(days=i)
        if next_day.weekday() in valid_day_numbers:
            return next_day
    return current_date + timedelta(days=7)  # fallback


@receiver(post_save, sender=Theme)
def group_level_update(sender, instance: Theme, created, **kwargs):
    if created:
        groups = Group.objects.filter(course=instance.course, level=instance.level)

        for group in groups:
            scheduled_days = group.scheduled_day_type.all()

            scheduled_day_numbers = [
                UZBEK_WEEKDAYS.index(day.name)
                for day in scheduled_days
                if day.name in UZBEK_WEEKDAYS
            ]

            if not scheduled_day_numbers:
                continue

            current_finish_date = group.finish_date
            new_finish_date = get_next_valid_day(
                current_finish_date, scheduled_day_numbers
            )

            if new_finish_date != current_finish_date:
                group.finish_date = new_finish_date
                group.save(update_fields=["finish_date"])
