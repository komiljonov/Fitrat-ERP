import os
import django
import random
from faker import Faker



# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "root.settings")  # Replace 'config.settings' with your actual settings path
django.setup()

# Import your models
from data.stages.models import NewLidStages, NewOredersStages, NewStudentStages, StudentStages
from data.lid.new_lid.models import Lid
from data.student.student.models import Student
from data.student.groups.models import Group, Day
from data.account.models import CustomUser
from data.department.filial.models import Filial
from data.student.attendance.models import Attendance
from data.student.lesson.models import Lesson
from data.student.subject.models import Subject
from data.department.marketing_channel.models import MarketingChannel
# Initialize Faker
fake = Faker()

# Generate Fake Data
def generate_fake_data():


    for _ in range(5):
        Filial.objects.create(
            name=fake.city(),
        )

    # Create NewLidStages objects
    NewLidStages.objects.create(name="NEW_LEAD")
    NewLidStages.objects.create(name="JARAYONDA")
    NewLidStages.objects.create(name="RAD ETDI")

    # Create NewOredersStages objects
    NewOredersStages.objects.create(name="FILIAL_BIRIKTIRILDI")
    NewOredersStages.objects.create(name="BIRINCHI SINOV DARSIGA YOZILDI")
    NewOredersStages.objects.create(name="SINOV DARSIGA KELMADI")
    NewOredersStages.objects.create(name="RAD ETDI")

    # Create NewStudentStages objects
    NewStudentStages.objects.create(name="TO'LOV KUTILMOQDA")
    NewStudentStages.objects.create(name="RAD ETDI")

    # Create StudentStages objects
    StudentStages.objects.create(name="ACTIVE TALABA")
    StudentStages.objects.create(name="QARIZDOR TALABA")
    StudentStages.objects.create(name="DARSNI TUXTATGAN")
    StudentStages.objects.create(name="KURSNI TUGATGAN")

    marketing  = ["Instagram","Telegram","Facebook ADD","Telegram bot","Fliyer"]
    for i in marketing:
        MarketingChannel.objects.create(
            name = i,
            type = f"{i} {fake.words()}",
        )

    day = ['Dushanba','Seshanba','Chorshanba',"Payshanba","Juma","Shanba","Yakshanba"]
    for i in day:
        Day.objects.create(
            name=i,
        )

    # Create Staff
    for _ in range(10):
        CustomUser.objects.create(
            full_name=fake.name(),
            phone=fake.phone_number(),
            role=random.choice([role[0] for role in CustomUser.ROLE_CHOICES]),
            balance=round(random.uniform(100000, 5000000), 100000),
        )

    # Create Students
    for _ in range(20):
        student = Student.objects.create(
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            phone_number=fake.phone_number(),
            date_of_birth=fake.date_of_birth(minimum_age=10, maximum_age=18),
            education_lang=random.choice(['ENG', 'RU', 'UZB']),
            edu_class=fake.random_int(min=1, max=12),
            subject=fake.word(),
            ball=fake.random_int(min=50, max=100),
            balance=round(random.uniform(100, 1000), 2),
            marketing_channel = MarketingChannel.objects.order_by("?").first(),
        )
        student.new_student_stages = NewStudentStages.objects.order_by('?').first()
        student.active_student_stages = StudentStages.objects.order_by('?').first()
        student.save()

    # Create Lids
    for _ in range(15):
        Lid.objects.create(
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            phone_number=fake.phone_number(),
            date_of_birth=fake.date_of_birth(minimum_age=20, maximum_age=40),
            education_lang=random.choice(['ENG', 'RU', 'UZB']),
            student_type="student",
            edu_class=fake.random_int(min=1, max=12),
            subject=fake.word(),
            ball=fake.random_int(min=50, max=100),
            filial=Filial.objects.order_by('?').first(),
            call_operator=CustomUser.objects.filter(role="CALL_OPERATOR").order_by('?').first(),
            lid_stages=NewLidStages.objects.order_by('?').first(),
            ordered_stages=NewOredersStages.objects.order_by('?').first(),
            marketing_channel=MarketingChannel.objects.order_by("?").first(),
        )

    # # Create Groups
    # for _ in range(5):
    #     # Create a Group instance
    #     group = Group.objects.create(
    #         name=f"Group {random.randint(1, 100)}",
    #         teacher=CustomUser.objects.filter(role="TEACHER").order_by('?').first(),
    #         price_type=random.choice(['DAILY', 'MONTHLY']),
    #         price=round(random.uniform(100, 500), 2),
    #         started_at=fake.date_time_this_year(before_now=True, after_now=False),  # Ensures a datetime object
    #         ended_at=fake.date_time_this_year(before_now=False, after_now=True),  # Ensures a datetime object
    #     )
    #
    #     # Assign random days to the scheduled_day_type field
    #     random_days = Day.objects.order_by('?')[:3]  # Select 3 random days
    #     group.scheduled_day_type.set(random_days)

    for _ in range(10):
        Lesson.objects.create(
            name=f"Lesson {fake.word()}",
            subject=Subject.objects.order_by('?').first(),
            group=Group.objects.order_by('?').first(),
            comment=fake.text(),
            lesson_status=random.choice([
                "ACTIVE","FINISHED"
            ]),
            lessons_count=fake.random_int(min=1, max=12),
        )

    for _ in range(50):
        Attendance.objects.create(
            lesson=Lesson.objects.order_by('?').first(),
            lid=Lid.objects.order_by('?').first(),
            reason=random.choice(["IS_PRESENT","REASONED","UNREASONED"]),
            remarks=fake.boolean(chance_of_getting_true=True)
        )

    print("Fake data generation completed!")

generate_fake_data()