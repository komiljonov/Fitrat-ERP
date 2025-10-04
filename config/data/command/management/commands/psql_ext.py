from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = "Enable required PostgreSQL extensions for ExclusionConstraint (btree_gist, btree_gin, etc.)"

    def handle(self, *args, **options):
        required_extensions = ["btree_gist", "btree_gin"]
        with connection.cursor() as cursor:
            for ext in required_extensions:
                self.stdout.write(self.style.NOTICE(f"Checking extension: {ext}"))
                cursor.execute(f"CREATE EXTENSION IF NOT EXISTS {ext};")
                self.stdout.write(self.style.SUCCESS(f"✓ Enabled: {ext}"))

        self.stdout.write(
            self.style.SUCCESS("All required PostgreSQL extensions are active.")
        )
