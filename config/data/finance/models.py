from django.contrib.auth import get_user_model
from django.db import models

from ..account.models import CustomUser
from ..command.models import TimeStampModel
from ..student.student.models import Student

User = get_user_model()

class Finance(TimeStampModel):
    action = models.CharField(
        choices=[
                ('INCOME', 'INCOME'),
                ('EXPENSE', 'EXPENSE'),
        ],
        default='INCOME',
        max_length=20,
    )

    amount = models.DecimalField(max_digits=10, decimal_places=2)

    kind = models.CharField(
        choices=[
            ('COURSE_PAYMENT', 'COURSE_PAYMENT'),
            ('SALARY', 'SALARY'),
            ('BONUS', 'BONUS'),
            ('MONEY_BACK', 'MONEY_BACK'),
            ('OTHER', 'OTHER'),
        ],
        default='COURSE_PAYMENT',
        max_length=20,
    )

    student : 'Student' = models.ForeignKey('student.Student', on_delete=models.SET_NULL,null=True,blank=True)

    stuff : 'CustomUser' = models.ForeignKey('account.CustomUser', on_delete=models.SET_NULL,null=True,blank=True,related_name='finance_stuff')

    creator : 'CustomUser' = models.ForeignKey("account.CustomUser", on_delete=models.SET_NULL,null=True,blank=True, related_name='finance_creator')

    def __str__(self):
        return f'{self.amount} {self.kind} {self.action}'




