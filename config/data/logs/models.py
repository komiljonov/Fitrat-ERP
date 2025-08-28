from django.db import models

from data.account.models import CustomUser
from data.command.models import BaseModel
from data.finances.finance.models import Finance
from data.lid.archived.models import Archived
from data.lid.new_lid.models import Lid
from data.results.models import Results
from data.student.lesson.models import FirstLLesson
from data.student.student.models import Student
from data.tasks.models import Task


class Log(BaseModel):
    app = models.CharField(
        choices=[
            ("Finance","Finance"),
            ("Account","Account"),
            ("Lid","Lid"),
            ("Archive","Archive"),
            ("Frozen","Frozen"),
            ("Clickuz","Clickuz"),
            ("Exam_results","Exam_results"),
            ("Parents","Parents"),
            ("Paycomuz","Paycomuz"),
            ("Results","Results"),
            ("Student","Student"),
            ("Tasks","Tasks"),
            ("Teachers","Teachers"),
            ("Upload","Upload")
        ], max_length=255,null=True,
        blank=True
    )

    model = models.CharField(max_length=255, null=True,blank=True)

    action = models.CharField(
        choices=[
            ("Finance", "Finance"),
            ("Log", "Log"),
        ], max_length=255,null=True,blank=True
    )

    model_action = models.CharField(
        choices=[
            ("Created", "Created"),
            ("Updated", "Updated"),
            ("Deleted", "Deleted"),
            ("Archived", "Archived"),
            ("Unarchived", "Unarchived"),
        ],max_length=255,null=True,blank=True
    )

    finance : "Finance" = models.ForeignKey(
        "finance.Finance",on_delete=models.SET_NULL,null=True,blank=True, related_name="log_finances"
    )
    lid : "Lid" = models.ForeignKey(
        "new_lid.Lid", on_delete=models.SET_NULL,null=True,blank=True, related_name="log_lids"
    )
    first_lessons : "FirstLLesson" = models.ForeignKey(
        "lesson.FirstLLesson", on_delete=models.SET_NULL,null=True,blank=True, related_name="log_first_lessons"
    )
    student : "Student" = models.ForeignKey(
        "student.Student", on_delete=models.SET_NULL,null=True,blank=True, related_name="log_students"
    )
    archive : "Archived" = models.ForeignKey(
        "archived.Archived",on_delete=models.SET_NULL,null=True,blank=True, related_name="log_archives"
    )
    account : "CustomUser" = models.ForeignKey(
        "account.CustomUser", on_delete=models.SET_NULL,null=True,blank=True, related_name="log_customuser"
    )
    result : "Results" = models.ForeignKey(
        "results.Results", on_delete=models.SET_NULL,null=True,blank=True, related_name="log_results"
    )
    task : "Task" = models.ForeignKey(
        "tasks.Task", on_delete=models.SET_NULL,null=True,blank=True, related_name="log_tasks"
    )

    comment = models.TextField(null=True,blank=True)
