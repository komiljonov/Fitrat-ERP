from django.db.models.signals import post_save
from django.dispatch import receiver

from ..new_lid.models import Lid
from ...parents.models import Relatives
from ...student.attendance.models import Attendance
from ...student.student.models import Student


@receiver(post_save, sender=Lid)
def on_details_create(sender, instance: Lid, created, **kwargs):
    """
    Signal to create or update a Student when a Lid is created or updated,
    provided `is_student=True` and `phone_number` is available.
    """
    if not created:
        if instance.is_student and instance.filial:
            import hashlib
            password_hash = hashlib.sha256("1".encode()).hexdigest()


            student, student_created = Student.objects.get_or_create(
                phone=instance.phone_number,
                defaults={
                    "first_name": instance.first_name,
                    "last_name": instance.last_name,
                    "password" : password_hash,
                    "middle_name": instance.middle_name,
                    "date_of_birth": instance.date_of_birth,
                    "education_lang": instance.education_lang,
                    "student_type": instance.student_type,
                    "edu_class": instance.edu_class,
                    "edu_level": instance.edu_level,
                    "subject": instance.subject,
                    "ball": instance.ball,
                    "filial": instance.filial,
                    "marketing_channel": instance.marketing_channel,
                    "call_operator": instance.call_operator,
                    "moderator": instance.moderator,
                },
            )

            # If the Student already exists, update their information
            if not student_created:
                student.first_name = instance.first_name
                student.last_name = instance.last_name
                student.middle_name = instance.middle_name
                student.date_of_birth = instance.date_of_birth
                student.password = password_hash
                student.education_lang = instance.education_lang
                student.student_type = instance.student_type
                student.edu_class = instance.edu_class
                student.edu_level = instance.edu_level
                student.subject = instance.subject
                student.ball = instance.ball
                student.filial = instance.filial
                student.marketing_channel = instance.marketing_channel
                student.call_operator = instance.call_operator
                student.moderator = instance.moderator
                student.save()

            # Update attendance records
            Attendance.objects.filter(lid=instance).update(student=student,lid=None)

            Relatives.objects.filter(lid=instance).update(student=student)
            # Archive the Lid
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
