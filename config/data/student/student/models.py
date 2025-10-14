from typing import TYPE_CHECKING, Literal
from datetime import datetime, timedelta
from decimal import Decimal

from django.db import models
from django.utils import timezone
from django.db.models import Q, F, Func
from django.contrib.postgres.constraints import ExclusionConstraint
from django.contrib.postgres.fields import RangeOperators

from data.command.models import BaseModel
from data.archive.models import Archive
from data.logs.models import Log


if TYPE_CHECKING:
    from data.lid.new_lid.models import Lid
    from data.student.studentgroup.models import StudentGroup
    from data.student.groups.models import Group
    from data.upload.models import File
    from data.department.marketing_channel.models import MarketingChannel
    from data.department.filial.models import Filial
    from data.student.subject.models import Level, Subject
    from data.parents.models import Relatives
    from data.account.models import CustomUser
    from data.employee.models import Employee


class Student(BaseModel):

    user: "CustomUser | None" = models.ForeignKey(
        "account.CustomUser",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="students_user",
    )

    photo = models.ForeignKey(
        "upload.File",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="students_photo",
    )

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100, null=True, blank=True)
    middle_name = models.CharField(max_length=100, null=True, blank=True)
    phone = models.CharField(max_length=100)
    date_of_birth = models.DateField(default=timezone.now)

    password = models.CharField(max_length=100, null=True, blank=True)

    language_choice = (("ENG", "ENG"), ("RU", "RU"), ("UZB", "UZB"))

    education_lang = models.CharField(
        choices=language_choice, default="UZB", max_length=100
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

    edu_level = models.CharField(null=True, blank=True, max_length=100)

    subject: "Subject | None" = models.ForeignKey(
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
        help_text="Earned ball at competition",
    )

    filial: "Filial" = models.ForeignKey(
        "filial.Filial",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="Filial for this student",
    )

    marketing_channel: "MarketingChannel" = models.ForeignKey(
        "marketing_channel.MarketingChannel",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="Marketing channel for this student",
    )

    # Student yangi o'quvchimi yoki, aktiv o'quvchimi?
    student_stage_type = models.CharField(
        choices=[
            ("NEW_STUDENT", "NEW_STUDENT"),
            ("ACTIVE_STUDENT", "ACTIVE_STUDENT"),
        ],
        default="NEW_STUDENT",
        max_length=100,
        help_text="Student yangi o'quvchimi yoki aktiv o'quvchimi?",
    )

    @property
    def status(self) -> Literal["NEW_STUDENT", "ACTIVE_STUDENT"]:

        return self.student_stage_type

    new_student_stages = models.CharField(
        choices=[
            ("BIRINCHI_DARS", "BIRNCHI_DARS"),
            ("BIRINCHI_DARSGA_KELMAGAN", "BIRINCHI_DARSGA_KELMAGAN"),
            ("GURUH_O'ZGARTIRGAN", "GURUH_O'ZGARTIRGAN"),
            ("QARIZDOR", "QARIZDOR"),
        ],
        null=True,
        blank=True,
        max_length=100,
        help_text="Student statusi",
    )

    balance = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal("0.00")
    )

    balance_status = models.CharField(
        choices=[
            ("ACTIVE", "ACTIVE"),
            ("INACTIVE", "INACTIVE"),
        ],
        default="INACTIVE",
        max_length=100,
        help_text="Balance status",
    )

    service_manager: "Employee" = models.ForeignKey(
        "employee.Employee",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="service_manager for this student",
        related_name="svm_students",
    )

    sales_manager: "Employee" = models.ForeignKey(
        "employee.Employee",
        on_delete=models.CASCADE,
        null=True,
    )

    is_frozen = models.BooleanField(
        default=False,
        help_text="Is this student frozen or not",
    )

    frozen_days = models.DateField(
        default=datetime.today,
        null=True,
        blank=True,
    )

    # new model fields for new freeze logic
    frozen_from_date = models.DateField(
        null=True, blank=True,
        help_text="This field defines when student was frozen")
    frozen_till_date = models.DateField(
        null=True, blank=True,
        help_text="This field defines when student becomes active after freeze period is finished")

    file: "File" = models.ManyToManyField(
        "upload.File",
        blank=True,
        related_name="student_files",
        help_text="File for this student",
    )

    call_operator: "CustomUser" = models.ForeignKey(
        "account.CustomUser",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Call operator",
        related_name="student_call_operator",
    )

    new_student_date = models.DateTimeField(null=True, blank=True)
    active_date = models.DateTimeField(null=True, blank=True)

    coins = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
    )
    points = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    groups: "models.QuerySet[StudentGroup]"
    relatives: "models.QuerySet[Relatives]"

    class Meta(BaseModel.Meta):
        ordering = ("is_frozen", "-created_at")

    def __str__(self):
        # return f"{self.first_name} {self.subject} {self.ball} in {self.student_stage_type} stage"
        return f"Student(id={self.id} name={self.first_name} {self.last_name} {self.middle_name} phone={self.phone})"

    def archive(self, comment: str = None, *, archived_by=None):

        Archive.objects.create(
            creator=archived_by,
            student=self,
            obj_status=self.student_stage_type,
            reason=comment,
        )

        self.archived_at = timezone.now()
        self.is_archived = True
        self.save()

        Log.objects.create(
            object="STUDENT",
            action="ARCHIVE_STUDENT",
            student=self,
            comment=f"O'quvchi arxiv'landi. Comment: {comment}",
        )

        if (
            self.service_manager
            and self.service_manager.f_svm_fine_student_archived > 0
        ):
            self.service_manager.transactions.create(
                reason="FINE_FOR_STUDENT_ARCHIVED",
                student=self,
                amount=self.service_manager.f_svm_fine_student_archived,
                comment="O'quvchi archivelangani uchun jarima.",
            )

        if (
            self.student_stage_type == "NEW_STUDENT"
            and self.sales_manager
            and self.sales_manager.f_sm_fine_new_student_archived
        ):
            self.sales_manager.transactions.create(
                reason="FINE_FOR_STUDENT_ARCHIVED",
                student=self,
                amount=self.sales_manager.f_sm_fine_new_student_archived,
                comment="Yangi o'quvchi archivelangani uchun jarima.",
            )

    def unarchive(self, comment: str = ""):
        now = timezone.now()
        cutoff = now - timedelta(hours=24)

        # Check if this student was archived within last 24 hours
        if self.archived_at and self.archived_at >= cutoff:
            self.archived_at = None
            self.is_archived = False
            self.save()

            Log.objects.create(
                object="STUDENT",
                action="UNARCHIVE_STUDENT",
                student=self,
                comment=f"O'quvchi arxivdan chiqarildi. Comment: {comment}",
            )

            # Unarchive related groups archived within last 24 hours
            groups = self.groups.filter(is_archived=True, archived_at__gte=cutoff)
            for group in groups:
                group.unarchive()  # assuming Group model also has .unarchive()
        else:
            Lid.objects.filter(
                first_name=self.first_name,
                last_name=self.last_name,
                middle_name=self.middle_name,
                phone_number=self.phone,
                date_of_birth=self.date_of_birth,
                education_lang=self.education_lang,
                student_type=self.student_type,
                edu_class=self.edu_class,
                edu_organization=self.edu_organization,
                edu_level=self.edu_level,
                subject=self.subject,
                ball=self.ball,
                filial=self.filial,
                marketing_channel=self.marketing_channel,
                lid_stage_type="ORDERED_LID",
                ordered_stages="YANGI_BUYURTMA",
                service_manager=self.service_manager,
                sales_manager=self.sales_manager,
            )


class FistLesson_data(BaseModel):

    teacher: "CustomUser" = models.ForeignKey(
        "account.CustomUser",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    group: "Group" = models.ForeignKey(
        "groups.Group",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    lesson_date = models.DateTimeField(null=True, blank=True)

    level: "Level" = models.ForeignKey(
        "subject.Level",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    lid: "Lid" = models.ForeignKey(
        "new_lid.Lid",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    class Meta(BaseModel.Meta):
        verbose_name = "Fist Lesson data"
        verbose_name_plural = "Fist Lesson data"


class StudentFrozenAction(BaseModel):
    student: "Student | None" = models.ForeignKey(
        "student.Student",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="frozen_actions",
    )
    from_date = models.DateField(
        null=True, blank=True,
        help_text="This field defines when student was frozen")
    till_date = models.DateField(
        null=True, blank=True,
        help_text="This field defines when student becomes active after freeze period is finished")
    reason = models.TextField(help_text="The reason why student has been frozen")

    class Meta(BaseModel.Meta):
        constraints = BaseModel.Meta.constraints + [
            models.UniqueConstraint(
                fields=["student"],
                condition=Q(is_archived=False),
                name="unique_active_freeze_per_student",
            ),
            models.CheckConstraint(
                check=Q(from_date__lt=F("till_date")),
                name="check_valid_freeze_dates",
            ),
            ExclusionConstraint(
                name="exclude_overlapping_freezes",
                expressions=[
                    (Func(F("from_date"), F("till_date"), function="tstzrange"), RangeOperators.OVERLAPS),
                    ("student", RangeOperators.EQ),

                ],
            ),
        ]