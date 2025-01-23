from django.db import models

# Create your models here.

from data.command.models import TimeStampModel


class Compensation(TimeStampModel):
    #When lead has gone to edu center branch this bonus will be given to call_operator
    call_center_lead = models.FloatField(default=0)

    administrator_first_lesson_come = models.FloatField(default=0)
    administrator_first_lesson_nt_come = models.FloatField(default=0)

    administrator_new_to_active_student = models.FloatField(default=0)
    administrator_new_to_active_student_nt = models.FloatField(default=0)



