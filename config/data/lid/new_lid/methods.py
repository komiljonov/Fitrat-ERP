import string
import random

from typing import TYPE_CHECKING
from datetime import datetime
from django.contrib.auth.hashers import make_password

from data.finances.finance.models import SaleStudent
from data.parents.models import Relatives
from data.student.attendance.models import Attendance
from data.student.student.models import Student
from data.student.studentgroup.models import SecondaryStudentGroup, StudentGroup

if TYPE_CHECKING:
    from data.lid.new_lid.models import Lid


class LeadMethods:

    def migrate_to_student(self: "Lid"):

        password = "".join(random.choices(string.ascii_letters + string.digits, k=8))

        student, student_created = Student.objects.get_or_create(
            phone=self.phone_number,
            defaults={
                "first_name": self.first_name,
                "last_name": self.last_name,
                "photo": self.photo,
                "password": make_password(password),
                "middle_name": self.middle_name,
                "date_of_birth": self.date_of_birth,
                "education_lang": self.education_lang,
                "student_type": self.student_type,
                "edu_class": self.edu_class,
                "edu_level": self.edu_level,
                "subject": self.subject,
                "balance": self.balance,
                "ball": self.ball,
                "filial": self.filial,
                "marketing_channel": self.marketing_channel,
                "call_operator": self.call_operator,
                "service_manager": self.service_manager,
                "sales_manager": self.sales_manager,
                "new_student_date": datetime.now(),
            },
        )

        # sms.send_sms(
        #     number=student.phone,
        #     message=f"""
        #     Fitrat Student ilovasiga muvaffaqiyatli ro‘yxatdan o‘tdingiz!

        #     Login: {student.phone}
        #     Parol: {password}

        #     Iltimos, ushbu ma’lumotlarni hech kimga bermang. Ilovaga kirib bolangizning natijalarini kuzatishingiz mumkin.
        #     """
        # )

        if not student_created:
            student.first_name = self.first_name
            student.last_name = self.last_name
            student.photo = self.photo
            student.middle_name = self.middle_name
            student.date_of_birth = self.date_of_birth
            student.password = make_password(password)
            student.education_lang = self.education_lang
            student.student_type = self.student_type
            student.edu_class = self.edu_class
            student.edu_level = self.edu_level
            student.subject = self.subject
            student.ball = self.ball
            student.filial = self.filial
            student.marketing_channel = self.marketing_channel
            student.call_operator = self.call_operator
            student.service_manager = self.service_manager
            student.sales_manager = self.sales_manager
            student.balance = (
                self.balance if self.balance == 0 else student.balance + self.balance
            )

            student.save()

            # sms.send_sms(
            #     number=student.phone,
            #     message=f"""
            #     Fitrat Student ilovasida muvaffaqiyatli ma'lumotlaringiz yangilandi!
            #
            #     Login: {student.phone}
            #     Parol: {password}
            #
            #     Iltimos, ushbu ma’lumotlarni hech kimga bermang. Ilovaga kirib bolangizning natijalarini kuzatishingiz mumkin.
            #     """
            # )

        StudentGroup.objects.filter(lid=self).update(student=student, lid=None)

        SecondaryStudentGroup.objects.filter(lid=self).update(student=student, lid=None)

        Attendance.objects.filter(lid=self).update(student=student, lid=None)

        SaleStudent.objects.filter(lid=self).update(student=student, lid=None)

        Relatives.objects.filter(lid=self).update(student=student)

        self.is_archived = True
        self.save()
