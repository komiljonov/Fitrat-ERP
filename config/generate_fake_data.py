# Set up Django environment
import os
import random

import django
from faker import Faker



os.environ.setdefault("DJANGO_SETTINGS_MODULE", "root.settings")
django.setup()

from data.stages.models import NewLidStages, NewOredersStages, NewStudentStages, StudentStages
from data.lid.new_lid.models import Lid
from data.student.student.models import Student
from data.student.groups.models import Day
from data.account.models import CustomUser
from data.department.filial.models import Filial
from data.department.marketing_channel.models import MarketingChannel
from data.student.subject.models import Subject
fake = Faker()

def generate_fake_data():
    # Filial
    for _ in range(5):
        Filial.objects.create(name=fake.city())

    # Stages
    stages = {
        'lid': ['NEW_LEAD', 'JARAYONDA', 'RAD ETDI'],
        'order': ['FILIAL_BIRIKTIRILDI', 'BIRINCHI SINOV DARSIGA YOZILDI', 'SINOV DARSIGA KELMADI', 'RAD ETDI'],
        'student': ['TO\'LOV KUTILMOQDA', 'RAD ETDI'],
        'active_student': ['ACTIVE TALABA', 'QARIZDOR TALABA', 'DARSNI TUXTATGAN', 'KURSNI TUGATGAN'],
    }

    for name in stages['lid']:
        NewLidStages.objects.create(name=name)
    for name in stages['order']:
        NewOredersStages.objects.create(name=name)
    for name in stages['student']:
        NewStudentStages.objects.create(name=name)
    for name in stages['active_student']:
        StudentStages.objects.create(name=name)

    # Marketing Channels
    marketing_channels = ['Instagram', 'Telegram', 'Facebook ADD', 'Telegram bot', 'Flyer']
    for channel in marketing_channels:
        MarketingChannel.objects.create(name=channel)

    # Days
    days = ['Dushanba', 'Seshanba', 'Chorshanba', 'Payshanba', 'Juma', 'Shanba', 'Yakshanba']
    for day in days:
        Day.objects.create(name=day)

    # CustomUser (Staff)
    roles = [role[0] for role in CustomUser.ROLE_CHOICES]
    for _ in range(10):
        CustomUser.objects.create(
            full_name=fake.name(),
            phone=fake.phone_number(),
            role=random.choice(roles),
            balance=round(random.uniform(100000, 5000000), 2),
        )

    # Students
    for _ in range(20):
        student = Student.objects.create(
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            phone=fake.phone_number(),
            date_of_birth=fake.date_of_birth(minimum_age=10, maximum_age=18),
            education_lang=random.choice(['ENG', 'RU', 'UZB']),
            edu_class=random.choice(["SCHOOL", "UNIVERSITY","NONE"]),
            edu_level=random.choice(["1", "10", "5", "7", "3", "2"]),
            subject=Subject.objects.order_by('?').first(),
            filial=Filial.objects.order_by('?').first(),
            ball=fake.random_int(min=50, max=100),
            balance=round(random.uniform(100, 1000), 2),
            marketing_channel=MarketingChannel.objects.order_by("?").first(),
            new_student_stages=NewStudentStages.objects.order_by('?').first(),
            active_student_stages=StudentStages.objects.order_by('?').first(),
        )

    # Lids
    for _ in range(15):
        Lid.objects.create(
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            phone_number=fake.phone_number(),
            date_of_birth=fake.date_of_birth(minimum_age=20, maximum_age=40),
            education_lang=random.choice(['ENG', 'RU', 'UZB']),
            student_type="student",
            edu_class=random.choice(["SCHOOL", "UNIVERSITY", "NONE"]),
            edu_level=random.choice(["1", "10", "5", "7", "3", "2"]),
            subject=Subject.objects.order_by('?').first(),
            ball=fake.random_int(min=50, max=100),
            filial=Filial.objects.order_by('?').first(),
            call_operator=CustomUser.objects.filter(role="CALL_OPERATOR").order_by('?').first(),
            lid_stages=NewLidStages.objects.order_by('?').first(),
            ordered_stages=NewOredersStages.objects.order_by('?').first(),
            marketing_channel=MarketingChannel.objects.order_by("?").first(),
        )

    print("Fake data generation completed!")

generate_fake_data()
