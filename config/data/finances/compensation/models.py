from typing import TYPE_CHECKING

from django.db import models

from data.command.models import BaseModel

if TYPE_CHECKING:
    from ...account.models import CustomUser


class Compensation(BaseModel):
    name = models.CharField(choices=[
        ("Sinov darsiga yozilb kemaganlar uchun jarima (Jarima)","Sinov darsiga yozilb kemaganlar uchun jarima (Jarima)"),
        (" Sinov darsiga keldi lekin activega o’tmaganligi uchun jarima (Jarima)",
         " Sinov darsiga keldi lekin activega o’tmaganligi uchun jarima (Jarima)"),
        ("Agar o’quvchi ketib qolsa jarima yoziladi (Jarima)","Agar o’quvchi ketib qolsa jarima yoziladi (Jarima)"),
        ("Jami qarzdor o'quvchilar sonining 80.1% dan 85% gacha bo'lgan qismi (Jarima)",
         "Jami qarzdor o'quvchilar sonining 80.1% dan 85% gacha bo'lgan qismi (Jarima)"),
        ("Jami qarzdor o'quvchilar sonining 70% dan 80.1% gacha bo'lgan qismi (Jarima)",
         "Jami qarzdor o'quvchilar sonining 70% dan 80.1% gacha bo'lgan qismi (Jarima)"),
        ("Jami qarzdor o'quvchilar sonining 70% dan kichik bo'lgan qismi (Jarima)",
         "Jami qarzdor o'quvchilar sonining 70% dan kichik bo'lgan qismi (Jarima)")
    ],max_length=256, null=True, blank=True)
    user: "CustomUser" = models.ForeignKey('account.CustomUser', on_delete=models.CASCADE)
    amount = models.DecimalField(decimal_places=2, max_digits=10)

    def __str__(self):
        return f"{self.name}  {self.amount}"


class Bonus(BaseModel):
    name = models.CharField(choices=[
        ("Markazga kelgan o‘quvchi uchun bonus","Markazga kelgan o‘quvchi uchun bonus"),
        ("Yaratilgan buyurtma uchun bonus","Yaratilgan buyurtma uchun bonus"),
        ("Sinov darsiga kelgani uchun bonus","Sinov darsiga kelgani uchun bonus"),
        ("Hizmat ko’rsatgan har bir Aktiv o'quvchi uchun bonus","Hizmat ko’rsatgan har bir Aktiv o'quvchi uchun bonus"),
        ("Aktiv o'quvchiga aylangan yangi o’quvchi uchun bonus","Aktiv o'quvchiga aylangan yangi o’quvchi uchun bonus"),
        ("Har bir qarzdor bo’lmagan va Aktiv o'quvchi uchun bonus","Har bir qarzdor bo’lmagan va Aktiv o'quvchi uchun bonus"),
        ("Jami yangi va aktiv o'quvchi o'quvchilarning 93% dan 94.9% gacha bo'lgan qismi uchun bonus",
         "Jami yangi va aktiv o'quvchi o'quvchilarning 93% dan 94.9% gacha bo'lgan qismi uchun bonus"),
        ("Jami yangi va aktiv o'quvchi o'quvchilarning 95% dan 97.9% gacha bo'lgan qismi uchun bonus",
         "Jami yangi va aktiv o'quvchi o'quvchilarning 95% dan 97.9% gacha bo'lgan qismi uchun bonus"),
        ("Jami yangi va aktiv o'quvchi o'quvchilarning 98% dan 99.9% gacha bo'lgan qismi uchun bonus",
         "Jami yangi va aktiv o'quvchi o'quvchilarning 98% dan 99.9% gacha bo'lgan qismi uchun bonus"),
        ("Jami yangi va aktiv o'quvchi o'quvchilarning 100% gacha bo'lgan qismi uchun bonus",
         "Jami yangi va aktiv o'quvchi o'quvchilarning 100% gacha bo'lgan qismi uchun bonus"),
        ("Aktiv o'quvchi soniga bonus","Aktiv o'quvchi soniga bonus"),
        ("Bir oyda 10 marta kelgan har bir oquvchi uchun bonus","Bir oyda 10 marta kelgan har bir oquvchi uchun bonus"),
        ("O’quvchi to’lagan summadan foiz beriladi","O’quvchi to’lagan summadan foiz beriladi")
    ],max_length=256, null=True,blank=True)
    user: "CustomUser" = models.ForeignKey('account.CustomUser', on_delete=models.CASCADE)
    amount = models.DecimalField(decimal_places=2, max_digits=10)

    def __str__(self):
        return f"{self.name}  {self.amount}"


class Page(BaseModel):
    user: "CustomUser" = models.ForeignKey('account.CustomUser', on_delete=models.CASCADE)
    name = models.CharField(max_length=256)
    is_editable = models.BooleanField(default=False)
    is_readable = models.BooleanField(default=False)

    is_parent = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name, self.is_editable, self.is_readable, self.is_parent}"


class Asos(BaseModel):
    name = models.CharField(max_length=256)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.name} "


class Comments(BaseModel):
    asos: "Asos" = models.ForeignKey('compensation.Asos', on_delete=models.CASCADE,
                                     related_name='asos4_comments')
    creator: "CustomUser" = models.ForeignKey('account.CustomUser', on_delete=models.CASCADE,
                                              related_name='asos4_creator_comments')
    user: "CustomUser" = models.ForeignKey('account.CustomUser', on_delete=models.CASCADE,
                                           related_name='asos4_user_comments')
    monitoring: "Monitoring" = models.ForeignKey('compensation.Monitoring', on_delete=models.CASCADE, )
    comment = models.TextField()

    def __str__(self):
        return f"{self.comment}"


class Point(BaseModel):
    name = models.CharField(max_length=256)
    asos: "Asos" = models.ForeignKey('compensation.Asos', on_delete=models.CASCADE)
    amount = models.FloatField(default=0, null=True, blank=True)
    max_ball = models.DecimalField(decimal_places=2, max_digits=10)


class Monitoring(BaseModel):
    creator: "CustomUser" = models.ForeignKey('account.CustomUser',
                                              on_delete=models.SET_NULL, null=True, blank=True,
                                              related_name="monitoring_creator")
    user: "CustomUser" = models.ForeignKey('account.CustomUser',
                                           on_delete=models.CASCADE, related_name='user_monitoring')
    point: "Point" = models.ForeignKey('compensation.Point',
                                       on_delete=models.CASCADE, related_name='point_monitoring')
    ball = models.CharField(max_length=128, null=True, blank=True,
                            help_text="This ball can not be higher than asos's max_ball !!!")

    counter = models.IntegerField()

    class Meta:
        verbose_name = "Monitoring"
        verbose_name_plural = "Monitoring 3, 12, 13, 14"

    def __str__(self):
        return f"{self.user.full_name}  {self.point.name}  {self.ball} / {self.point.max_ball}"


class ResultName(BaseModel):
    name = models.CharField(max_length=256)
    point_type = models.CharField(choices=[
        ('Percentage', 'Percentage'),
        ('Ball', 'Ball'),
        ('Degree', 'Degree')],
        max_length=10
    )
    type = models.CharField(choices=[
        ("One", "One"),
        ("Two", "Two"),
    ], max_length=10, null=True, blank=True)

    class Meta:
        verbose_name = "Natijalar"
        verbose_name_plural = "Natijalar monitoringi"

    def __str__(self):
        return f"{self.name}"


class ResultSubjects(BaseModel):
    asos: "Asos" = models.ForeignKey('compensation.Asos', on_delete=models.CASCADE)
    result: "ResultName" = models.ForeignKey('compensation.ResultName',
                                             on_delete=models.SET_NULL,
                                             null=True, blank=True)
    name = models.CharField(max_length=256)
    result_type = models.CharField(choices=[
        ("Mine", "Mine"),
        ("Student", "Student"),
    ], max_length=256, null=True, blank=True)
    point = models.CharField(max_length=10, null=True, blank=True)
    max_ball = models.CharField(max_length=128, null=True, blank=True)

    level = models.CharField(choices=[
        ("Region", "Region"),
        ("Regional", "Regional"),
    ], max_length=256, null=True, blank=True)

    university_type = models.CharField(choices=[
        ("Personal", "Personal"),
        ("National", "National"),
    ], max_length=256, null=True, blank=True)

    from_point = models.CharField(max_length=10, null=True, blank=True)
    to_point = models.CharField(max_length=10, null=True, blank=True)

    amount = models.CharField(max_length=128, null=True, blank=True)

    class Meta:
        verbose_name = "Monitoring"
        verbose_name_plural = "Natija turi"

    def __str__(self):
        return f"{self.name}"


class MonitoringAsos4(BaseModel):
    asos = models.ForeignKey('compensation.Asos', on_delete=models.SET_NULL, null=True, blank=True)
    creator: "CustomUser" = models.ForeignKey('account.CustomUser',
                                              on_delete=models.SET_NULL, null=True, blank=True,
                                              related_name="MonitoringAsos4_creator_comments")
    result_frk = models.ForeignKey('results.Results', on_delete=models.SET_NULL, null=True, blank=True)
    result = models.ForeignKey('compensation.ResultName', on_delete=models.SET_NULL, null=True, blank=True)
    user: "CustomUser" = models.ForeignKey('account.CustomUser', on_delete=models.SET_NULL, null=True, blank=True)
    subject = models.ForeignKey('compensation.ResultSubjects', on_delete=models.SET_NULL, null=True, blank=True)
    ball = models.CharField(max_length=128, null=True, blank=True)

    class Meta:
        verbose_name = "Monitoring 4"
        verbose_name_plural = "Monitoring 4"

    def __str__(self):
        return f"{self.user.full_name} - {self.asos.name} - {self.subject.name}"


class StudentCountMonitoring(BaseModel):
    asos: "Asos" = models.ForeignKey('compensation.Asos', on_delete=models.CASCADE)
    max_ball = models.DecimalField(decimal_places=2, max_digits=10)
    amount = models.FloatField(default=0, null=True, blank=True)
    teacher = models.ForeignKey('account.CustomUser', on_delete=models.SET_NULL,
                                null=True, blank=True, related_name="student_count_monitoring_teacher")

    type = models.CharField(choices=[
        ("PENALTY", "PENALTY"),
        ("BONUS", "BONUS"),
    ], max_length=20, null=True, blank=True)

    from_point = models.CharField(max_length=256, null=True, blank=True)
    to_point = models.CharField(max_length=256, null=True, blank=True)

    class Meta:
        verbose_name = "Monitoring"
        verbose_name_plural = "O'quvchini soni monitoringi"

    def __str__(self):
        return f"{self.from_point} - {self.to_point}"


class Monitoring5(BaseModel):
    ball = models.DecimalField(decimal_places=2, max_digits=10)
    student_count = models.CharField(max_length=10, null=True, blank=True)
    teacher: "CustomUser" = models.ForeignKey('account.CustomUser', on_delete=models.SET_NULL,
                                              null=True, blank=True, related_name="Monitoring5_creator_comments")

    class Meta:
        verbose_name = "Monitoring 5"
        verbose_name_plural = "Monitoring 5"

    def __str__(self):
        return f"{self.teacher.full_name}  {self.student_count} - {self.ball}"


class StudentCatchingMonitoring(BaseModel):
    asos: "Asos" = models.ForeignKey('compensation.Asos', on_delete=models.CASCADE)
    teacher: "CustomUser" = models.ForeignKey('account.CustomUser', on_delete=models.SET_NULL,
                                              null=True, blank=True, related_name="StudentCatchingMonitoring_teacher")
    name = models.CharField(max_length=256)
    from_student = models.CharField(max_length=256)
    to_student = models.CharField(max_length=256, null=True, blank=True)
    type = models.CharField(choices=[
        ("Bonus", "Bonus"),
        ("Compensation", "Compensation"),
    ], max_length=256)
    ball = models.FloatField(default=0, null=True, blank=True)

    class Meta:
        verbose_name = "Monitoring"
        verbose_name_plural = "O'quvchini olib qolish monitoringi"

    def __str__(self):
        return f"{self.name} {self.type}"
