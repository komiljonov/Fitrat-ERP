from django.contrib.auth import get_user_model
from django.db import models

from ..new_lid.models import Lid
from ...command.models import TimeStampModel
User = get_user_model()
class Archived(TimeStampModel):
    creator : User = models.ForeignKey(User, on_delete=models.CASCADE,related_name='archived_students')
    lid : Lid = models.ForeignKey(Lid, on_delete=models.CASCADE)

    reason = models.TextField()

    def __str__(self):
        return self.lid.first_name + " " + self.lid.last_name

