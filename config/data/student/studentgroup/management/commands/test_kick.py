from django.core.management.base import BaseCommand

from data.student.studentgroup.tasks import check_for_streak_students


class Command(BaseCommand):

    def handle(self, *args, **options):

        print("Running")

        check_for_streak_students()

        print("End")
