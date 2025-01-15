from django.db import models

from config.data.lid.new_lid.models import Lid
from config.data.student.lesson.models import Lesson
from config.data.student.student.models import Student


class Attendance(models.Model):
    lesson : Lesson = models.ForeignKey('lesson.Lesson', on_delete=models.CASCADE)
    if lesson.lesson_status == "FIRST_LESSON" or lesson.lesson_status == "SECOND_LESSON":
        lid : Lid = models.ForeignKey('lid.Lid', on_delete=models.CASCADE)
    student : Student = models.ForeignKey('student.Student', on_delete=models.CASCADE)

    REASON_CHOICES = [
        ('IS_PRESENT', 'Is Present'),
        ('REASONED', 'Sababli'),
        ('UNREASONED', 'Sababsiz'),
    ]
    reason = models.CharField(
        max_length=20,
        choices=REASON_CHOICES,
        default='UNREASONED',
        help_text="Attendance reason (Sababli/Sababsiz)"
    )
    remarks : str = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.lesson} for {self.lid if self.lid else self.student} is marked as {self.reason}"