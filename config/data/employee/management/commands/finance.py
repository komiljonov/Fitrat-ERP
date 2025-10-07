from typing import Any
from django.core.management.base import BaseCommand
from tqdm import tqdm

from data.employee.models import Employee


class Command(BaseCommand):

    def handle(self, *args: Any, **options: Any) -> str | None:

        employees = Employee.objects.filter(role="ACCOUNTING")

        for employee in tqdm(employees):
            employee.calculate_monthly_salary()
