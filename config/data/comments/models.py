from django.contrib.auth import get_user_model
from django.db import models

from ..command.models import TimeStampModel

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..lid.new_lid.models import Lid
    from ..student.student.models import Student
    from ..account.models import CustomUser

class Comment(TimeStampModel):

    creator : "CustomUser" = models.ForeignKey('account.CustomUser', on_delete=models.CASCADE)
    lid : 'Lid' = models.ForeignKey('new_lid.Lid', on_delete=models.CASCADE, null=True,blank=True)
    student : 'Student' = models.ForeignKey('student.Student', on_delete=models.CASCADE, null=True,blank=True)
    comment : str = models.TextField()

    def __str__(self):
        return self.comment

    class Meta:
        ordering = []