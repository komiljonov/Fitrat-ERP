from django.db import models

from ..command.models import TimeStampModel

class NewLidStages(TimeStampModel):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class NewOredersStages(TimeStampModel):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class NewStudentStages(TimeStampModel):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class StudentStages(TimeStampModel):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
