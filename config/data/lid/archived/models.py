from django.contrib.auth import get_user_model
from django.db import models

from ..new_lid.models import Lid
from ...command.models import TimeStampModel
from ...student.student.models import Student

from ...account.models import CustomUser


class Archived(TimeStampModel):
    creator : "CustomUser" = models.ForeignKey('account.CustomUser', on_delete=models.CASCADE,
                                               related_name='archived_user')
    lid : "Lid" = models.ForeignKey('new_lid.Lid', on_delete=models.SET_NULL,
                                    null=True, blank=True, related_name='archived_lead')
    student : "Student" = models.ForeignKey('student.Student', on_delete=models.SET_NULL,
                                            null=True, blank=True, related_name='archived_students')
    reason = models.TextField()

    def __str__(self):
        return (self.lid.first_name if self.lid else self.student.first_name)+ " " + (self.lid.last_name if self.lid else self.student.last_name)

