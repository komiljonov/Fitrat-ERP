
import os

import django
from faker import Faker

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "root.settings")
django.setup()

from data.student.groups.models import Day
from data.account.models import CustomUser
from data.department.marketing_channel.models import MarketingChannel, Group_Type
from data.finances.compensation.models import Page, Asos
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
      "employees_data",
      "employees_archive",
      "control",
      "monitoring_page",
      "settings",
      "results",
      "shop",
    ]
    for i in pages:
        Page.objects.create(
            user=CustomUser.objects.filter(phone="+998901234567").first(),
            name=i,
            is_readable=True,
            is_editable=True,
        )

    asos = [
        "ASOS_1",
        "ASOS_2",
        "ASOS_3",
        "ASOS_4",
        "ASOS_5",
        "ASOS_6",
        "ASOS_7",
        "ASOS_8",
        "ASOS_9",
        "ASOS_10",
        "ASOS_11",
        "ASOS_12",
        "ASOS_13",
        "ASOS_14",
    ]
    for i in asos:
        Asos.objects.create(
            name=i,
        )

    marketing_channels = {
        "Tanishlar orqali": "#FF5733",
        "Instagram": "#33FF57",
        "Telegram": "#3357FF",
        "Facebook reklamasi": "#F4A261",
        "Flayer": "#9B5DE5",
        "Olimpiadalar": "#00C9A7",
        "Reklama bannerlar va doskalari": "#E63946",
        "Loyihalardan": "#FDCB58",
        "Web site": "#9B5DE5"
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
        "Salary": ("EXPENSE", "#FF5733"),  # Bright Red-
        "Voucher" : ("EXPENSE","#3498DB"),
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

    print("Fake data generation completed!")

generate_fake_data()
