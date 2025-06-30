from django.contrib.auth import get_user_model
from django.db import models

from ..new_lid.models import Lid
from ...command.models import BaseModel
from ...student.student.models import Student
from ...comments.views import Comment


from ...account.models import CustomUser


class Archived(BaseModel):
    creator : "CustomUser" = models.ForeignKey('account.CustomUser', on_delete=models.CASCADE,
                                               related_name='archived_user')
    lid : "Lid" = models.ForeignKey('new_lid.Lid', on_delete=models.SET_NULL,
                                    null=True, blank=True, related_name='archived_lead')
    student : "Student" = models.ForeignKey('student.Student', on_delete=models.SET_NULL,
                                    null=True, blank=True, related_name='archived_students')
    reason = models.TextField()

    comment : "Comment" = models.ForeignKey('comments.Comment',
                                    on_delete=models.SET_NULL,null=True,blank=True,related_name='archived_comments')
    is_archived = models.BooleanField(default=False)

    def __str__(self):
        return (self.lid.first_name if self.lid else self.student.first_name)+ " " + (self.lid.last_name if self.lid else self.student.last_name)

