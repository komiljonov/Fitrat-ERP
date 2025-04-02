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

    def __str__(self):
        return f"{self.student.phone}  -- {self.point} point"


class Coins(BaseModel):
    coin = models.IntegerField(default=0)
    student : "Student" = models.ForeignKey("student.Student", on_delete=models.SET_NULL, null=True, blank=True, related_name="coins_of_student")
    is_exchanged = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.student.phone}  -- {self.coin} coin"


class Products(BaseModel):
    name = models.CharField(max_length=120)
    coin = models.IntegerField(default=0)
    image : "File" = models.ForeignKey("upload.File", on_delete=models.SET_NULL, null=True, blank=True, related_name="product_image")

    def __str__(self):
        return f"{self.name} -- {str(self.coin)}"

class Shop(BaseModel):
    product : "Products" = models.ForeignKey("shop.Products", on_delete=models.SET_NULL, null=True, blank=True, related_name="shops_product")
    student : "Student" = models.ForeignKey("student.Student", on_delete=models.SET_NULL, null=True, blank=True, related_name="shops_customer")

    def __str__(self):
        return f"{self.student.phone}  -- {self.product}"