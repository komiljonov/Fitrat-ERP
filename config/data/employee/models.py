from data.account.models import CustomUser
from data.employee.manager import EmployeeManager


# Create your models here.


class Employee(CustomUser):

    objects = EmployeeManager()

    class Meta:
        proxy = True
