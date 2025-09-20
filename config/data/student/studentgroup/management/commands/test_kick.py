from django.core.management.base import BaseCommand

from data.student.student.models import Student
from data.student.studentgroup.tasks import check_for_streak_students


class Command(BaseCommand):

    def handle(self, *args, **options):

        print("Running")

        s = Student.objects.filter(id="2097747b-d703-4235-a6d2-896dac2681a9").first()

        sg = s.groups.first()

        print(sg.streak())

        # check_for_streak_students()

        print("End")
