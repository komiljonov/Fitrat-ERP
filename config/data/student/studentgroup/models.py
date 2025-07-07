from django.db import models

from data.command.models import BaseModel
from data.lid.new_lid.models import Lid
from data.student.groups.models import Group, SecondaryGroup
from data.student.student.models import Student


class StudentGroup(BaseModel):
    group: "Group" = models.ForeignKey('groups.Group', on_delete=models.SET_NULL, null=True, blank=True,
                                       related_name="student_groups")
    student: "Student" = models.ForeignKey('student.Student', on_delete=models.SET_NULL, null=True, blank=True,
                                           related_name="students_group")
    lid: "Lid" = models.ForeignKey('new_lid.Lid', on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name="lids_group")

    is_archived : bool = models.BooleanField(default=False)

    homework_type = models.CharField(choices=[
        ("Online", "Online"),
        ("Offline", "Offline"),
    ],default="Offline",null=True,blank=True,max_length=20)

    class Meta:
        verbose_name = "Add Group"
        verbose_name_plural = "Add Groups"

    def __str__(self):
        return self.group.name if self.group else ""


class SecondaryStudentGroup(BaseModel):
    group: "SecondaryGroup" = models.ForeignKey('groups.SecondaryGroup',
                                                on_delete=models.SET_NULL, null=True, blank=True)
    student: "Student" = models.ForeignKey('student.Student', on_delete=models.SET_NULL,
                                           related_name="students_secondary_group", null=True, blank=True)
    lid: "Lid" = models.ForeignKey('new_lid.Lid', on_delete=models.SET_NULL,
                                   related_name="lids_secondary_group", null=True, blank=True)

    class Meta:
        verbose_name = "Secondary Add group"
        verbose_name_plural = "Secondary Add group"
