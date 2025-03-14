from django.db import models

from data.command.models import TimeStampModel
from data.student.groups.models import Group , SecondaryGroup
from data.student.student.models import Student
from data.lid.new_lid.models import Lid


# Create your models here.
class StudentGroup(TimeStampModel):
    group: "Group" = models.ForeignKey('groups.Group', on_delete=models.SET_NULL, null=True, blank=True,
                                       related_name="student_groups")
    student: "Student" = models.ForeignKey('student.Student', on_delete=models.SET_NULL, null=True, blank=True,
                                           related_name="students_group")
    lid: "Lid" = models.ForeignKey('new_lid.Lid', on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name="lids_group")

    def __str__(self):
        return self.group.name if self.group else ""


class SecondaryStudentGroup(TimeStampModel):
    group: "SecondaryGroup" = models.ForeignKey('groups.SecondaryGroup',
                                                on_delete=models.SET_NULL, null=True, blank=True)
    student: "Student" = models.ForeignKey('student.Student', on_delete=models.SET_NULL,
                                           related_name="students_secondary_group", null=True, blank=True)
    lid: "Lid" = models.ForeignKey('new_lid.Lid', on_delete=models.SET_NULL,
                                   related_name="lids_secondary_group", null=True, blank=True)

    def __str__(self):
        return self.group.name
