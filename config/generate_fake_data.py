# Set up Django environment
import os
import random

import django
from faker import Faker



os.environ.setdefault("DJANGO_SETTINGS_MODULE", "root.settings")
django.setup()

from data.student.groups.models import Day
from data.account.models import CustomUser
from data.department.filial.models import Filial
from data.department.marketing_channel.models import MarketingChannel
from data.finances.compensation.models import Page
from data.finances.finance.models import Kind
fake = Faker()

def generate_fake_data():

    pages = [
      "reports",
      "admin_report",
      "edu_report",
      "monitoring",
      "finance_report",
      "leads",
      "new_leads",
      "orders",
      "archived_leads",
      "students",
      "new_students",
      "active_students",
      "archived_students",
      "all_students",
      "edu_section",
      "materials",
      "subjects",
      "levels",
      "courses",
      "themes",
      "groups",
      "rooms",
      "schedule",
      "cashiers",
      "tasks",
      "employees",
      "control"
    ]
    for i in pages:
        Page.objects.create(
            user=CustomUser.objects.filter(phone="+998901234567").first(),
            name=i,
            is_readable=True,
            is_editable=True,
        )

    marketing_channels = {
        "Tanishlar orqali": "#FF5733",  # Bright Red-Orange
        "Instagram": "#33FF57",  # Vibrant Green
        "Telegram": "#3357FF",  # Deep Blue
        "Facebook reklamasi": "#F4A261",  # Warm Sand
        "Flayer": "#9B5DE5",  # Purple Glow
        "Olimpiadalar": "#00C9A7",  # Teal Mint
        "Reklama bannerlar va doskalari": "#E63946",  # Coral Red
        "Loyihalardan": "#FDCB58",  # Golden Yellow
    }

    for name, color in marketing_channels.items():
        MarketingChannel.objects.get_or_create(
            name=name,
            defaults={"type": color}
        )

    # Days
    days = ['Yakshanba','Shanba', 'Juma','Payshanba','Chorshanba','Seshanba','Dushanba',]
    for day in days:
        Day.objects.create(name=day)

    kind_actions = {
        "Salary": ("EXPENSE", "#FF5733"),  # Bright Red-Orange
        "Bonus": ("EXPENSE", "#33FF57"),  # Vibrant Green
        "Course payment": ("INCOME", "#3357FF"),  # Deep Blue
        "Lesson payment": ("INCOME", "#F4A261"),  # Warm Sand
        "Money back": ("EXPENSE", "#9B5DE5"),  # Purple Glow
        "CASHIER_HANDOVER": ("EXPENSE", "#00C9A7"),  # Teal Mint
        "CASHIER_ACCEPTANCE": ("INCOME", "#E63946"),  # Coral Red
    }

    for name, (action, color) in kind_actions.items():
        Kind.objects.get_or_create(
            name=name,
            defaults={"action": action, "color": color}
        )

    # # CustomUser (Staff)
    # roles = [role[0] for role in CustomUser.ROLE_CHOICES]
    # for _ in range(10):
    #     CustomUser.objects.create(
    #         full_name=fake.name(),
    #         phone=fake.phone_number(),
    #         role=random.choice(roles),
    #         balance=round(random.uniform(100000, 5000000), 2),
    #     )

    # # Students
    # for _ in range(20):
    #     Student.objects.create(
    #         first_name=fake.first_name(),
    #         last_name=fake.last_name(),
    #         phone=fake.phone_number(),
    #         date_of_birth=fake.date_of_birth(minimum_age=10, maximum_age=18),
    #         education_lang=random.choice(['ENG', 'RU', 'UZB']),
    #         edu_class=random.choice(["SCHOOL", "UNIVERSITY","NONE"]),
    #         edu_level=random.choice(["1", "10", "5", "7", "3", "2"]),
    #         subject=Subject.objects.order_by('?').first(),
    #         filial=Filial.objects.order_by('?').first(),
    #         ball=fake.random_int(min=50, max=100),
    #         balance=round(random.uniform(100000, 1000000),5),
    #         marketing_channel=MarketingChannel.objects.order_by("?").first(),
    #         student_stage_type=random.choice(['NEW_STUDENT','ACTIVE_STUDENT']),
    #         new_student_stages=random.choice(['BIRINCHI_DARS',"GURUH_O'ZGARTIRGAN","QARIZDOR"])
    #     )
    #
    # # Lids
    # for _ in range(15):
    #     Lid.objects.create(
    #         first_name=fake.first_name(),
    #         last_name=fake.last_name(),
    #         phone_number=fake.phone_number(),
    #         date_of_birth=fake.date_of_birth(minimum_age=20, maximum_age=40),
    #         education_lang=random.choice(['ENG', 'RU', 'UZB']),
    #         student_type="student",
    #         edu_class=random.choice(["SCHOOL", "UNIVERSITY", "NONE"]),
    #         edu_level=random.choice(["1", "10", "5", "7", "3", "2"]),
    #         subject=Subject.objects.order_by('?').first(),
    #         ball=fake.random_int(min=50, max=100),
    #         filial=Filial.objects.order_by('?').first(),
    #         call_operator=CustomUser.objects.filter(role="CALL_OPERATOR").order_by('?').first(),
    #         lid_stages=NewLidStages.objects.order_by('?').first(),
    #         ordered_stages=NewOredersStages.objects.order_by('?').first(),
    #         marketing_channel=MarketingChannel.objects.order_by("?").first(),
    #     )

    print("Fake data generation completed!")

generate_fake_data()
