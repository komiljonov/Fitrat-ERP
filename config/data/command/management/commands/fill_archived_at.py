from django.core.management.base import BaseCommand
from django.utils import timezone


from data.command.models import BaseModel


class Command(BaseCommand):
    help = "Sync archived_at field with is_archived for all BaseModel subclasses"

    def handle(self, *args, **options):
        models = BaseModel.__subclasses__()

        for model in models:
            print("Updating", model.__name__)
            # archived = True → archived_at = now (only if not already set)
            updated_archived = model.objects.filter(
                is_archived=True, archived_at__isnull=True
            ).update(archived_at=timezone.now())

            # archived = False → archived_at = NULL
            updated_unarchived = model.objects.filter(
                is_archived=False, archived_at__isnull=False
            ).update(archived_at=None)

            self.stdout.write(
                f"{model.__name__}: "
                f"{updated_archived} set archived_at, "
                f"{updated_unarchived} cleared archived_at"
            )
