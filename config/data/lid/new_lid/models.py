from typing import TYPE_CHECKING

from decimal import Decimal
from django.db import models

from data.command.models import BaseModel
from data.lid.new_lid.methods import LeadMethods

if TYPE_CHECKING:
    from data.department.marketing_channel.models import MarketingChannel
    from data.student.studentgroup.models import StudentGroup
    from data.department.filial.models import Filial
    from data.student.student.models import Student
    from data.account.models import CustomUser
    from data.upload.models import File
    from data.finances.finance.models import SaleStudent
    from data.student.attendance.models import Attendance
    from data.student.studentgroup.models import SecondaryStudentGroup
    from data.parents.models import Relatives
    from data.firstlesson.models import FirstLesson
    from data.employee.models import Employee


class Lid(BaseModel, LeadMethods):

    sender_id = models.CharField(max_length=500, null=True, blank=True)
    message_text = models.CharField(max_length=500, null=True, blank=True)

    photo: "File" = models.ForeignKey(
        "upload.File",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="lids_photo",
    )

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100, null=True, blank=True)
    middle_name = models.CharField(max_length=100, null=True, blank=True)
    phone_number = models.CharField(max_length=100, null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    extra_number = models.CharField(max_length=100, null=True, blank=True)

    LANGUAGE_CHOICES = (
        ("ENG", "ENG"),
        ("RU", "RU"),
        ("UZB", "UZB"),
    )

    education_lang = models.CharField(
        choices=LANGUAGE_CHOICES,
        default="UZB",
        max_length=100,
    )

    student_type = models.CharField(max_length=100, default="student")

    edu_class = models.CharField(
        choices=[
            ("SCHOOL", "School"),
            ("UNIVERSITY", "University"),
            ("MATURE", "Mature"),
            ("NONE", "None"),
        ],
        default="NONE",
        max_length=100,
        help_text="Education level at school if student studies at school",
    )

    edu_organization = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Education organization, school or university or work.",
    )

    edu_level = models.CharField(
        null=True,
        blank=True,
        max_length=100,
        help_text="O'quvchining bilib darajasi.",
    )

    subject = models.ForeignKey(
        "subject.Subject",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Subject that student won at competition",
    )

    ball = models.IntegerField(
        default=0,
        null=True,
        blank=True,
        help_text="Earned balls at competition.",
    )

    filial: "Filial | None" = models.ForeignKey(
        "filial.Filial",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Filial for this student.",
    )

    marketing_channel: "MarketingChannel | None" = models.ForeignKey(
        "marketing_channel.MarketingChannel",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    lid_stage_type = models.CharField(
        choices=(
            ("NEW_LID", "NEW_LID"),
            ("ORDERED_LID", "ORDERED_LID"),
        ),
        max_length=100,
        default="NEW_LID",
    )

    lid_stages = models.CharField(
        choices=[
            ("YANGI_LEAD", "YANGI_LEAD"),
            ("KUTULMOQDA", "KUTULMOQDA"),
        ],
        max_length=100,
        help_text="LID's YANGI_LEAD stage type",
        null=True,
        blank=True,
    )

    is_expired = models.BooleanField(default=False)

    ordered_stages = models.CharField(
        choices=[
            ("KUTULMOQDA", "KUTULMOQDA"),
            ("BIRINCHI_DARS_BELGILANGAN", "BIRINCHI_DARS_BELGILANGAN"),
            ("YANGI_BUYURTMA", "YANGI_BUYURTMA"),
        ],
        max_length=100,
        help_text="LID's YANGI_LEAD stage type",
        null=True,
        blank=True,
    )

    is_double = models.BooleanField(
        default=False,
        help_text="Is this Lead duble or not",
    )

    is_frozen = models.BooleanField(
        default=False,
        help_text="Is this Lead frozen or not",
    )

    call_operator: "Employee" = models.ForeignKey(
        "employee.Employee",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="CallOperator for this lid",
        related_name="call_operator",
    )

    is_student = models.BooleanField(
        default=False,
        help_text="Is this student or not",
    )

    service_manager: "CustomUser" = models.ForeignKey(
        "account.CustomUser",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="service_manager",
    )

    sales_manager: "CustomUser" = models.ForeignKey(
        "account.CustomUser",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="sales_manager",
    )

    file: "File" = models.ManyToManyField(
        "upload.File",
        blank=True,
        related_name="lid_files",
    )

    ordered_date = models.DateTimeField(null=True, blank=True)

    student: "Student | None" = models.ForeignKey(
        "student.Student",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="lid_student",
    )

    balance = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    first_lesson_created_at = models.DateTimeField(null=True, blank=True)

    sales: "models.QuerySet[SaleStudent]"
    attendances: "models.QuerySet[Attendance]"
    groups: "models.QuerySet[StudentGroup]"
    secondary_groups: "models.QuerySet[SecondaryStudentGroup]"
    relatives: "models.QuerySet[Relatives]"
    first_lessons: "models.QuerySet[FirstLesson]"

    def __str__(self):
        return (
            f"{self.first_name} {self.subject} {self.ball} in {self.lid_stages} stage"
        )
