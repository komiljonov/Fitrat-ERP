from django.db import models

from ...command.models import TimeStampModel

from ...upload.models import File
from ...student.groups.models import Group


class Subject(TimeStampModel):
    name = models.CharField(max_length=100)
    label = models.CharField(max_length=100, blank=True, null=True)
    has_level = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name}  has level  {self.has_level}"



class Level(TimeStampModel):
    name = models.CharField(max_length=100)
    def __str__(self):
        return self.name




class Theme(TimeStampModel):

    subject : 'Subject' = models.ForeignKey('subject.Subject', on_delete=models.CASCADE)

    title = models.CharField(max_length=100)
    description = models.TextField()

    type = models.CharField(choices=[
        ('HOMEWORK', 'HOMEWORK'),
        ('COURSE_WORK', 'COURSE_WORK'),
        ('EXTRA', 'EXTRA'),
    ],
    default='HOMEWORK',
    max_length=100,)

    group: "Group" = models.ForeignKey(
        "groups.Group", on_delete=models.CASCADE, related_name="courses_themes"
    )

    video : 'File' = models.ForeignKey('upload.File', on_delete=models.SET_NULL, null=True,blank=True,
                                       related_name='videos',)
    file : 'File' = models.ForeignKey('upload.File', on_delete=models.SET_NULL, null=True,blank=True,
                                      related_name='files')
    photo : 'File' = models.ForeignKey('upload.File', on_delete=models.SET_NULL, null=True,blank=True,
                                       related_name='photos')

    def __str__(self):
        return f"{self.subject} - {self.title}  {self.type}"
