from django.db import models

from data.account.models import CustomUser
from data.command.models import TimeStampModel
from data.lid.new_lid.models import Lid
from data.student.student.models import Student

class Casher(TimeStampModel):
    name = models.CharField(max_length=100)
    user: "CustomUser" = models.ForeignKey(
        'account.CustomUser',
        on_delete=models.CASCADE,
        related_name='finances',
    )
    role = models.CharField(
        choices=[
            ('ADMINISTRATOR', 'ADMINISTRATOR'),
            ('WEALTH', 'WEALTH'),
            ("ACCOUNTANT", "ACCOUNTANT"),
        ],
        default='ADMINISTRATOR',
        max_length=20,
    )
    def __str__(self):
        return f"{self.user.phone} {self.role}"

class Finance(TimeStampModel):

    casher : "Casher" = models.ForeignKey(
        'finance.Casher',
        on_delete=models.CASCADE,
        related_name='finances_casher',
    )

    action = models.CharField(
        choices=[
                ('INCOME', 'INCOME'),
                ('EXPENSE', 'EXPENSE'),
        ],
        default='INCOME',
        max_length=20,
    )

    amount = models.FloatField(default=0)

    kind = models.CharField(
        choices=[
            ('COURSE_PAYMENT', 'COURSE_PAYMENT'),
            ('SALARY', 'SALARY'),
            ('BONUS', 'BONUS'),
            ('MONEY_BACK', 'MONEY_BACK'),
            ('OTHER', 'OTHER'),
            ('CASHIER_HANDOVER', 'Kassa topshirish'),
            ('CASHIER_ACCEPTANCE', 'Kassa qabul qilish'),
        ],
        default='COURSE_PAYMENT',
        max_length=20,
    )

    student : 'Student' = models.ForeignKey('student.Student', on_delete=models.SET_NULL,null=True,blank=True)

    lid : 'Lid' = models.ForeignKey('new_lid.Lid', on_delete=models.SET_NULL,null=True,blank=True)

    stuff : 'CustomUser' = models.ForeignKey('account.CustomUser', on_delete=models.SET_NULL,null=True,blank=True,related_name='finance_stuff')

    creator : 'CustomUser' = models.ForeignKey("account.CustomUser", on_delete=models.SET_NULL,null=True,blank=True, related_name='finance_creator')

    comment = models.TextField(null=True, blank=True)


    def __str__(self):
        return f'{self.amount} {self.kind} {self.action}'






