from django.db import models


from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from data.student.course.models import Course
from ...command.models import BaseModel
from ...upload.models import File


class Subject(BaseModel):
    name = models.CharField(max_length=100)
    label = models.CharField(max_length=100, blank=True, null=True)
    image = models.ForeignKey("upload.File", on_delete=models.SET_NULL, null=True, blank=True)
    has_level = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name}  has level  {self.has_level}"



class Level(BaseModel):
    subject : "Subject" = models.ForeignKey("subject.Subject",
                                            on_delete=models.SET_NULL,null=True,blank=True)
    name = models.CharField(max_length=100)
    courses : "Course" = models.ForeignKey("course.Course",on_delete=models.SET_NULL,null=True,blank=True,related_name="levels_course")
    class Meta:
        ordering = ['created_at']
    def __str__(self):
        return self.name


class Theme(BaseModel):
    subject = models.ForeignKey('subject.Subject', on_delete=models.CASCADE)

    title = models.TextField(null=True, blank=True)
    description = models.TextField()

    theme = models.CharField(
        choices=[
            ('Lesson', 'Lesson'),
            ('Repeat', 'Repeat'),
        ],
        default='Lesson',
        max_length=100
    )

    repeated_theme = models.ManyToManyField(
        "subject.Theme",blank=True,related_name="theme_repeated_theme",
    )

    course = models.ForeignKey(
        "course.Course", on_delete=models.CASCADE, related_name="courses_themes"
    )

    level : "Level" = models.ForeignKey(
        "subject.Level", on_delete=models.SET_NULL,null=True,blank=True, 
        related_name="themes_level"
    )

    # Separate fields for different types of work within the same Theme
    homework_files = models.ManyToManyField(
        'upload.File',  blank=True, related_name='theme_homework_files'
    )
    course_work_files = models.ManyToManyField(
        'upload.File',  blank=True, related_name='theme_course_work_files'
    )
    extra_work_files = models.ManyToManyField(
        'upload.File',  blank=True, related_name='theme_extra_work_files'
    )

    # General media fields
    videos = models.ManyToManyField(
        'upload.File',  blank=True, related_name='theme_videos'
    )
    files = models.ManyToManyField(
        'upload.File',  blank=True, related_name='theme_files'
    )
    photos = models.ManyToManyField(
        'upload.File',  blank=True, related_name='theme_photos'
    )


    class Meta:
        ordering = ('created_at',)
    def __str__(self):
        return f"{self.subject} - {self.title}"
