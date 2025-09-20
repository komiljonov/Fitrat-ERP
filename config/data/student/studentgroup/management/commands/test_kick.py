from django.core.management.base import BaseCommand

from data.student.student.models import Student
from data.student.studentgroup.tasks import check_for_streak_students


class Command(BaseCommand):

    def handle(self, *args, **options):

        print("Running")

        s = Student.objects.filter(id="2097747b-d703-4235-a6d2-896dac2681a9").first()

        for sg in s.groups.all():
            print(f"Streak for group: {sg.group.name}: {sg.streak()}")

        # sg = s.groups.filter(id="2963b48c-6b94-4494-b2a9-5f863c24f283").first()

        check_for_streak_students()

        print("End")
