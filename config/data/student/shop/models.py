from decimal import Decimal

from django.db import models

from data.command.models import BaseModel
from ..student.models import Student
from ...upload.models import File


class Points(BaseModel):
    point = models.IntegerField(default=0)
    from_test = models.ForeignKey("mastering.Mastering", on_delete=models.SET_NULL, null=True, blank=True, related_name="point_from_test")
    from_homework = models.ForeignKey("homeworks.Homework", on_delete=models.SET_NULL, null=True, blank=True, related_name="point_from_homework")
    is_exchanged = models.BooleanField(default=False)

    student : "Student" = models.ForeignKey("student.Student", on_delete=models.SET_NULL, null=True, blank=True, related_name="points_of_student")

    comment = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.student.phone}  -- {self.point} point"


class Coins(BaseModel):
    coin = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    student : "Student" = models.ForeignKey("student.Student", on_delete=models.SET_NULL, null=True,
                                            blank=True, related_name="coins_of_student")

    comment = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.student.phone}  -- {self.coin} coin"


class Category(BaseModel):
    name = models.CharField(max_length=120)
    def __str__(self):
        return self.name

class Products(BaseModel):
    name = models.CharField(max_length=120)
    comment = models.TextField(blank=True, null=True)
    coin = models.IntegerField(default=0)
    category : "Category" = models.ForeignKey("shop.Category", on_delete=models.SET_NULL, null=True, blank=True, related_name="product_category")
    image : "File" = models.ManyToManyField("upload.File",related_name="product_image")

    def __str__(self):
        return f"{self.name} -- {str(self.coin)}"

class Purchase(BaseModel):
    product : "Products" = models.ForeignKey("shop.Products", on_delete=models.SET_NULL,
                                             null=True, blank=True, related_name="purchases_product")
    student : "Student" = models.ForeignKey("student.Student", on_delete=models.SET_NULL,
                                            null=True, blank=True, related_name="purchases_customer")
    status = models.CharField(choices=[("Pending", "Pending"), ("Completed", "Completed")], max_length=20,default="Pending")

    def __str__(self):
        return f"{self.student.phone}  -- {self.product}"

