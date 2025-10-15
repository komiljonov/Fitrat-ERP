from data.student.groups.models import Group
from django.core.management import BaseCommand

from data.student.groups.utils import calculate_finish_date


class Command(BaseCommand):

    def handle(self, *args, **kwargs):

        groups = Group.objects.all()

        for group in groups:

            finish_date_after_repeated = calculate_finish_date(
                course=group.course,
                level=group.level,
                week_days=group.scheduled_day_type.all(),
                start_date=group.start_date,
            )

            group.finish_date = finish_date_after_repeated
            group.save()
