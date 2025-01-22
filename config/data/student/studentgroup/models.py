from idlelib.query import Query

from django.db import models
from django.db.models import QuerySet

from data.command.models import TimeStampModel
from data.student.groups.models import Group
from data.student.student.models import Student
from data.lid.new_lid.models import Lid

# Create your models here.
class StudentGroup(TimeStampModel):
    group : "Group" = models.ForeignKey('groups.Group', on_delete=models.CASCADE, related_name="student_groups")
    student : "Student" = models.ForeignKey('account.CustomUser', on_delete=models.SET_NULL,null=True,blank=True)
    lead : "Lid" = models.ForeignKey('new_lid.Lid', on_delete=models.SET_NULL,null=True,blank=True)


    def __str__(self):
        return self.group.name
