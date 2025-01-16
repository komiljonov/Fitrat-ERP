from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.template.context_processors import request

from ..new_lid.models import Lid
from ...student.student.models import Student
from ...stages.models import NewStudentStages

@receiver(post_save, sender=Lid)
def on_details_create(sender, instance: Lid, created, **kwargs):
    """
    Signal to create or update a Student when a Lid is created or updated,
    provided `is_student=True` and `phone_number` is available.
    """
    if not created:
        if instance.is_student and instance.filial:
            # Get the default `NewStudentStages` instance
            new_student_stage_instance = NewStudentStages.objects.first()
            print(new_student_stage_instance)
            if not new_student_stage_instance:
                raise ValueError("No NewStudentStages instances found in the database.")

            # Check if a Student with the same phone number exists
            student, student_created = Student.objects.get_or_create(
                phone_number=instance.phone_number,
                defaults={
                    "first_name": instance.first_name,
                    "last_name": instance.last_name,
                    "date_of_birth": instance.date_of_birth,
                    "education_lang": instance.education_lang,
                    "student_type": instance.student_type,
                    "edu_class": instance.edu_class,
                    "subject": instance.subject,
                    "ball": instance.ball,
                    "filial": instance.filial,
                    "marketing_channel": instance.marketing_channel,
                    "new_student_stages": new_student_stage_instance,  # Assign instance here
                    "call_operator": instance.call_operator,
                    "moderator": instance.moderator,
                }
            )

            # If the Student already exists, update their information
            if not student_created:
                student.first_name = instance.first_name
                student.last_name = instance.last_name
                student.date_of_birth = instance.date_of_birth
                student.education_lang = instance.education_lang
                student.student_type = instance.student_type
                student.edu_class = instance.edu_class
                student.subject = instance.subject
                student.ball = instance.ball
                student.filial = instance.filial
                student.marketing_channel = instance.marketing_channel
                student.new_student_stages = new_student_stage_instance  # Assign instance here
                student.call_operator = instance.call_operator
                student.moderator = instance.moderator
                student.save()

            post_save.disconnect(on_details_create, sender=Lid)
            instance.is_archived = True
            instance.save()
            post_save.connect(on_details_create, sender=Lid)

        else:
            if instance.filial is None:
                print("This lead's education branch is not updated, please add education branch.")

            post_save.disconnect(on_details_create, sender=Lid)
            instance.save()
            post_save.connect(on_details_create, sender=Lid)


