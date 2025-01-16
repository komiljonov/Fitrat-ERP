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
from data.student.groups.models import Group
from data.account.models import CustomUser

# Initialize Faker
fake = Faker()

# Generate Fake Data
def generate_fake_data():
    # Create Stages
    for _ in range(10):
        NewLidStages.objects.create(name=fake.word())
        NewOredersStages.objects.create(name=fake.word())
        NewStudentStages.objects.create(name=fake.word())
        StudentStages.objects.create(name=fake.word())

    # Create Staff
    for _ in range(10):
        CustomUser.objects.create(
            full_name=fake.name(),
            phone=fake.phone_number(),
            role=random.choice([role[0] for role in CustomUser.ROLE_CHOICES]),
            balance=round(random.uniform(1000, 5000), 2),
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
            lid_stages=NewLidStages.objects.order_by('?').first(),
            ordered_stages=NewOredersStages.objects.order_by('?').first(),
            is_archived=fake.boolean(),
        )

    # Create Groups
    for _ in range(5):
        Group.objects.create(
            name=f"Group {fake.word()}",
            teacher=CustomUser.objects.filter(role="TEACHER").order_by('?').first(),
            price_type=random.choice(['DAILY', 'MONTHLY']),
            price=round(random.uniform(100, 500), 2),
            scheduled_day_type=random.choice(['EVERYDAY', 'ODD', 'EVEN']),
            started_at=fake.date_this_year(before_today=True, after_today=False),
            ended_at=fake.date_this_year(before_today=False, after_today=True),
        )

    print("Fake data generation completed!")

generate_fake_data()