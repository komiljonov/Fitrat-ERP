from django.db import models
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..subject.models import Theme
from ...command.models import TimeStampModel
from ...lid.new_lid.models import Lid
from ...student.student.models import Student


class Attendance(TimeStampModel):
    theme : 'Theme' = models.ForeignKey('subject.Theme', on_delete=models.CASCADE)
    lid : 'Lid' = models.ForeignKey('new_lid.Lid', on_delete=models.SET_NULL,null=True,blank=True)
    student : 'Student' = models.ForeignKey('student.Student', on_delete=models.SET_NULL,null=True,blank=True)

    REASON_CHOICES = [
        ('IS_PRESENT', 'Is Present'),
        ('REASONED', 'Sababli'),
        ('UNREASONED', 'Sababsiz'),
        ('HOLIDAY','Dam olish kuni'),
    ]
    reason = models.CharField(
        max_length=20,
        choices=REASON_CHOICES,
        default='UNREASONED',
        help_text="Attendance reason (Sababli/Sababsiz)"
    )
    remarks : str = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.theme.type} for {self.lid.first_name if self.lid else self.student.first_name} is marked as {self.reason}"



