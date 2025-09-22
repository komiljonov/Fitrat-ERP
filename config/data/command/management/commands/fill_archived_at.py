from django.core.management.base import BaseCommand

from data.command.models import BaseModel


class Command(BaseCommand):

    def handle(self, *args, **options):

        models = BaseModel.__subclasses__()

        for model in models:
            print(model.__name__, model.objects.count())
