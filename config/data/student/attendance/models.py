from django.db import models
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..subject.models import Theme
from ...command.models import BaseModel
from ...lid.new_lid.models import Lid
from ...student.student.models import Student
from ...student.groups.models import Group


class Attendance(BaseModel):
    theme : 'Theme' = models.ManyToManyField('subject.Theme', blank=True,related_name='attendance_theme')
    group : "Group" = models.ForeignKey('groups.Group', on_delete=models.CASCADE,
                                        null=True, blank=True, related_name='attendance_group')
    repeated = models.BooleanField(default=False)
    lid : 'Lid' = models.ForeignKey('new_lid.Lid', on_delete=models.SET_NULL,null=True,blank=True,
                                    related_name='attendance_lid')
    student : 'Student' = models.ForeignKey('student.Student', on_delete=models.SET_NULL,null=True,blank=True,
                                            related_name='attendance_student')

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

    amount = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Attendance counted amount ..."
    )

    def __str__(self):
        return f" {self.group} is marked as {self.reason}"



