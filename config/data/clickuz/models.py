from django.db import models
from data.lid.new_lid.models import Lid
from data.student.student.models import Student

# Create your models here.


class Transaction(models.Model):
    PROCESSING = 'processing'
    FINISHED = 'finished'
    CANCELED = 'canceled'
    STATUS = ((PROCESSING, PROCESSING), (FINISHED, FINISHED), (CANCELED, CANCELED))
    click_trans_id = models.CharField(max_length=255)
    merchant_trans_id = models.CharField(max_length=255)
    amount = models.CharField(max_length=255)
    action = models.CharField(max_length=255)
    sign_string = models.CharField(max_length=255)
    sign_datetime = models.DateTimeField(max_length=255)
    status = models.CharField(max_length=25, choices=STATUS, default=PROCESSING)

    def __str__(self):
        return self.click_trans_id



class Order(models.Model):
    lid : "Lid" = models.ForeignKey("new_lid.Lid", on_delete=models.SET_NULL, null=True, blank=True, related_name="ordered_lid")
    student : "Student" = models.ForeignKey("student.Student", on_delete=models.SET_NULL, null=True, blank=True, related_name="ordered_student")
    type : str = models.CharField(choices=[
        ("Payme","Payme"),
        ("Click","Click"),
    ],max_length=255,null=True,blank=True)
    amount = models.CharField(max_length=255)
    paid = models.BooleanField(default=False)