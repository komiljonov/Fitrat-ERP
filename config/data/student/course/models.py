from ..subject.models import *

# Create your models here.
class Course(BaseModel):
    name = models.CharField(max_length=100)

    subject : Subject = models.ForeignKey('subject.Subject', on_delete=models.CASCADE)
    level: 'Level' = models.ForeignKey('subject.Level', on_delete=models.SET_NULL, null=True,blank=True)
    lessons_number = models.CharField(max_length=100,null=True, blank=True,help_text="Number of lessons")

    theme : 'Theme' = models.ManyToManyField('subject.Theme', related_name='courses',blank=True)

    status = models.CharField(
        choices=[
            ('ACTIVE', 'Active'),
            ('INACTIVE', 'Inactive'),
        ],
        default='INACTIVE',
        max_length=100,
    )

    def __str__(self):
        return f"{self.name} {self.subject} {self.status}"