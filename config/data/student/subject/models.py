from django.db import models

from ...command.models import TimeStampModel

from ...upload.models import File



class Subject(TimeStampModel):
    name = models.CharField(max_length=100)
    label = models.CharField(choices=[
        ("RED", 'RED'),
        ("GREEN", 'GREEN'),
        ("BLUE", 'BLUE'),
        ("YELLOW", 'YELLOW'),
        ("PURPLE", 'PURPLE'),
        ("CYAN", 'CYAN'),
        ("MAGENTA", 'MAGENTA'),
        ("GRAY", 'GRAY'),
        ("BLACK", 'BLACK'),
        ("WHITE", 'WHITE'),
    ], max_length=100
    )

    def __str__(self):
        return self.name



class Level(TimeStampModel):
    name = models.CharField(max_length=100)
    def __str__(self):
        return self.name




class Theme(TimeStampModel):

    subject : 'Subject' = models.ForeignKey('subject.Subject', on_delete=models.CASCADE)

    title = models.CharField(max_length=100)
    description = models.TextField()
    video : 'File' = models.ForeignKey('upload.File', on_delete=models.SET_NULL, null=True,
                                       related_name='videos')
    file : 'File' = models.ForeignKey('upload.File', on_delete=models.SET_NULL, null=True,
                                      related_name='files')
    photo : 'File' = models.ForeignKey('upload.File', on_delete=models.SET_NULL, null=True,
                                       related_name='photos')


    type = models.CharField(choices=[
        ('HOMEWORK', 'HOMEWORK'),
        ('COURSE_WORK', 'COURSE_WORK'),
        ('EXTRA', 'EXTRA'),
    ],
    default='HOMEWORK',
    max_length=100,)
    def __str__(self):
        return f"{self.subject} - {self.title}  {self.type}"
