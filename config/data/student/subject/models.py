from django.db import models


from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from data.student.course.models import Course
from ...command.models import TimeStampModel
from ...upload.models import File


class Subject(TimeStampModel):
    name = models.CharField(max_length=100)
    label = models.CharField(max_length=100, blank=True, null=True)
    has_level = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name}  has level  {self.has_level}"



class Level(TimeStampModel):
    subject : "Subject" = models.ForeignKey("subject.Subject",
                                            on_delete=models.SET_NULL,null=True,blank=True)
    name = models.CharField(max_length=100)
    def __str__(self):
        return self.name


class Theme(TimeStampModel):
    subject = models.ForeignKey('subject.Subject', on_delete=models.CASCADE)

    title = models.CharField(max_length=100)
    description = models.TextField()

    theme = models.CharField(
        choices=[
            ('Lesson', 'Lesson'),
            ('Repeat', 'Repeat'),
        ],
        default='Lesson',
        max_length=100
    )

    course = models.ForeignKey(
        "course.Course", on_delete=models.CASCADE, related_name="courses_themes"
    )

    # Separate fields for different types of work within the same Theme
    homework_files = models.ManyToManyField(
        'upload.File', null=True, blank=True, related_name='theme_homework_files'
    )
    course_work_files = models.ManyToManyField(
        'upload.File', null=True, blank=True, related_name='theme_course_work_files'
    )
    extra_work_files = models.ManyToManyField(
        'upload.File', null=True, blank=True, related_name='theme_extra_work_files'
    )

    # General media fields
    videos = models.ManyToManyField(
        'upload.File', null=True, blank=True, related_name='theme_videos'
    )
    files = models.ManyToManyField(
        'upload.File', null=True, blank=True, related_name='theme_files'
    )
    photos = models.ManyToManyField(
        'upload.File', null=True, blank=True, related_name='theme_photos'
    )

    def __str__(self):
        return f"{self.subject} - {self.title}"
