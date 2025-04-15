from django.db import models

from data.account.models import CustomUser
from data.command.models import BaseModel
from data.lid.new_lid.models import Lid
from data.student.attendance.models import Attendance
from data.student.student.models import Student


class Casher(BaseModel):
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

class Kind(BaseModel):
    action = models.CharField(
        choices=[
                ('INCOME', 'INCOME'),
                ('EXPENSE', 'EXPENSE'),
        ],
        default='INCOME',
        max_length=20,
    )
    name = models.CharField(max_length=100)
    color = models.CharField(
        max_length=100,
        null=True,
        blank=True,
    )

    def __str__(self):
        return f"{self.action} {self.name}"

class PaymentMethod(BaseModel):
    name = models.CharField(max_length=100)
    def __str__(self):
        return f"{self.name}"

class Finance(BaseModel):

    casher : "Casher" = models.ForeignKey(
        'finance.Casher',
        on_delete=models.SET_NULL,
        related_name='finances_casher',
        null=True,
        blank=True,
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

    kind : "Kind"= models.ForeignKey(
        "finance.Kind",on_delete=models.SET_NULL,
        related_name='finances_kind',
        null=True,blank=True
    )

    payment_method = models.CharField(
        choices=[
            ('Click', 'Click'),
            ('Payme', 'Payme'),
            ('Cash','Naqt pul'),
            ('Card','Card'),
            ('Money_send',"Pul o'tkazish")
        ],default='Payme',max_length=100,null=True,blank=True
    )

    attendance : "Attendance" = models.ForeignKey('attendance.Attendance',on_delete=models.SET_NULL,null=True,blank=True,
                                   related_name='attendance_finances')

    student : 'Student' = models.ForeignKey('student.Student', on_delete=models.SET_NULL,null=True,blank=True)

    lid : 'Lid' = models.ForeignKey('new_lid.Lid', on_delete=models.SET_NULL,null=True,blank=True)

    stuff : 'CustomUser' = models.ForeignKey('account.CustomUser', on_delete=models.SET_NULL,null=True,blank=True,related_name='finance_stuff')

    creator : 'CustomUser' = models.ForeignKey("account.CustomUser", on_delete=models.SET_NULL,null=True,blank=True, related_name='finance_creator')

    comment = models.TextField(null=True, blank=True)

    is_first = models.BooleanField(default=False,null=True,blank=True)

    is_given = models.BooleanField(default=False,null=True,blank=True)

    def __str__(self):
        return f'{self.amount}  {self.action}'

class Handover(BaseModel):
    casher : "Casher" = models.ForeignKey(
        'finance.Casher',
        on_delete=models.CASCADE,
        related_name='finances_casher_handover',
    )
    receiver : "Casher" = models.ForeignKey(
        'finance.Casher',
        on_delete=models.CASCADE,
        related_name='finances_receiver_handover',
    )
    amount = models.FloatField(default=0)

    def __str__(self):
        return f'{self.casher} {self.receiver} {self.amount}'

class KpiFinance(BaseModel):
    user: "CustomUser" = models.ForeignKey(
        'account.CustomUser',
        on_delete=models.CASCADE,
    )
    lid : "Lid" = models.ForeignKey(
        'new_lid.Lid',on_delete=models.SET_NULL,null=True,blank=True,related_name='finances_kpi_lid'
    )
    student : "Student" = models.ForeignKey(
        'student.Student',on_delete=models.SET_NULL,null=True,blank=True,related_name='finances_kpi_student'
    )

    reason = models.CharField(
        max_length=100,null=True,blank=True,
    )
    amount = models.FloatField(default=0)

    type = models.CharField(
        choices=[
            ('INCOME', 'INCOME'),
            ('EXPENSE', 'EXPENSE'),
        ],
        default='INCOME',
        max_length=20,
    )
    def __str__(self):
        return f"{self.user.phone} {self.type} {self.amount}"

class Voucher(BaseModel):
    creator: "CustomUser" = models.ForeignKey(
        'account.CustomUser',
        on_delete=models.CASCADE,
        related_name='finances_voucher_creator',
    )
    name = models.CharField(
        max_length=100,
        null=True,
        blank=True,
    )
    amount = models.FloatField(default=0, max_length=100)

    count = models.IntegerField(default=0)

    is_expired = models.BooleanField(default=False)
    lid : "Lid" = models.ForeignKey(
        'new_lid.Lid',
        on_delete=models.SET_NULL,
        related_name='finances_voucher_lid',
        null=True,
        blank=True,
    )
    student : "Student" = models.ForeignKey(
        'student.Student',
        on_delete=models.SET_NULL,
        related_name='finances_voucher_student',
        null=True,
        blank=True,
    )

    def __str__(self):
        return f"{self.creator} {self.amount} {self.is_expired}"

class Sale(BaseModel):
    creator : "CustomUser" = models.ForeignKey(
        'account.CustomUser',
        on_delete=models.CASCADE,
        related_name='finances_creator_sale',
    )
    name = models.CharField(
        max_length=100,
        null=True,
        blank=True,
    )
    status = models.CharField(
        choices=[
            ("ACTIVE", "ACTIVE"),
            ("EXPIRED", "EXPIRED"),
        ],
        max_length=20,
        null=True,
        blank=True,
        default='ACTIVE',
    )
    amount = models.FloatField(default=0)

    def __str__(self):
        return f"{self.creator.phone}  {self.status} {self.amount}"

class SaleStudent(BaseModel):
    creator : "CustomUser" = models.ForeignKey(
        'account.CustomUser',
        on_delete=models.CASCADE,
        related_name='finances_creator_student_sale',
    )
    sale : "Sale" = models.ForeignKey(
        'finance.Sale',
        on_delete=models.CASCADE,
        related_name='finances_sale_student',
    )
    student : "Student" = models.ForeignKey(
        'student.Student',
        on_delete=models.SET_NULL,
        related_name='finances_student_sale',
        null=True,
        blank=True,
    )
    lid : "Lid" = models.ForeignKey(
        'new_lid.Lid',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    expire_date = models.DateField(null=True,blank=True)
    comment = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.creator.phone} {self.sale.amount} to {self.student.phone if self.student else self.lid.phone_number if self.lid else None}"

class VoucherStudent(BaseModel):
    creator : "CustomUser" = models.ForeignKey(
        'account.CustomUser',
        on_delete=models.CASCADE,
        related_name='finances_creator_student_voucher',
    )
    voucher : "Voucher" = models.ForeignKey(
        'finance.Voucher',
        on_delete=models.CASCADE,
        related_name='finances_voucher_voucher',
    )
    student : "Student" = models.ForeignKey(
        'student.Student',
        on_delete=models.SET_NULL,
        related_name='finances_student_voucher',
        null=True,
        blank=True,
    )
    lid : "Lid" = models.ForeignKey(
        'new_lid.Lid',
        on_delete=models.SET_NULL,
        related_name='finances_lid_voucher',
        null=True,
        blank=True,
    )
    comment = models.TextField(null=True, blank=True)
    def __str__(self):
        return (f"{self.student.phone if self.student else self.lid.phone_number}"
                f"{self.voucher.name} {self.created_at}")
