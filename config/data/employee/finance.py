from typing import TYPE_CHECKING

from django.db import models

from data.command.models import BaseModel

from django.contrib.postgres.constraints import ExclusionConstraint
from django.contrib.postgres.fields import DecimalRangeField
from django.contrib.postgres.fields.ranges import RangeOperators

from django.core.exceptions import ValidationError


if TYPE_CHECKING:
    from data.employee.models import Employee


"""1. Operator
   1.1. Operator buyurtma yaratgandan keyin, sinov darsiga otsa bonus yoziladi.
2. Sotuv manageri
    2.1. Sinov darsi belgilangani uchun bonus. 
    2.2. Sinov darsiga kelgani uchun bonus.
    2.3. Yengi aktib oquvchi uchun bonus. 100.000 dan kop tolov qilsa, aktivga o'tadi.
    2.4. Agarda sinov darsi archive'ga o'tib ketib qolsa, jarima yoziladi.
    2.5. Yangi o'quvchidan archive'ga ketsa, jarima.
3. Service manager
    3.1. Har oyni ohirida, service managerga har bitta aktiv o'quvchi uchun bonus yozilishi kerak.
    3.2. Archivega ketgani uchun jarima.
4. Moliya manageri - har oyni boshida.
    4.1. Qarzdor bolmagan o'quvchilar foiziga qarab turib, shu foizlarga kors hsr bitta qarzdor bo'lmagan o'quvchilar uchun bonus yoziladi.
    4.2. Agarda qanchadur foizdan tushib ketsa, har bitta qarzdorlar uchun shtraf. 
5. Davomatchi, filial bosh manageri, monitoringchi, testolog. - aynan ozini filialida
    5.1. Har oyji birinchi sanasida, har bitta aktiv oquvchi uchun bonus.
6. Head teacher va filial rahbari 2 3 ta filialda ishlashi mumkin, va 5.1 daka bonus oladi.
7. O'qituvchi.
    7.1. Har bitta darsga yechilgan puldan, qanchadur foiz olinadi. O'quvchidan yechilgan paytda.
    7.2. Sinov darsiga kelib, lekin aktivga o'tmasdan ketib qolsa, yoki boshqa o'qituvchiga o'tib ketib qolsa. Yoki boshqa filialga ketib qolsa. Jarima yoziladi.
    7.3. 
    


1. Sinovdigi o'quvchi to'lov qilib, darsga kegan vaqtida 100.000 so'mdan ko'p balansi bo'lsa, pramoy aktivga o'tishi kerak. Davomatdan keyin.
2."""


class EmployeeFinanceFields(models.Model):

    ###############################################
    ##     Operator uchun bonus va jarimalar     ##
    ###############################################
    f_op_bonus_create_order = models.IntegerField(
        default=0,
        help_text="Operator buyurtma yaratgani uchun bonus.",
    )

    #####################################################
    ##     Sotuv manageri uchun bonus va jarimalar     ##
    #####################################################

    f_sm_bonus_create_first_lesson = models.IntegerField(
        default=0,
        help_text="Sotuv manageri sinov darsi yaratgani uchun bonus.",
    )
    f_sm_bonus_first_lesson_come = models.IntegerField(
        default=0,
        help_text="O'quvchi sinov darsiga kelgani uchun Sotuv manageriga bonus.",
    )
    f_sm_bonus_new_active_student = models.IntegerField(
        default=0,
        help_text="O'quvchi aktiv holatiga o'tgani uchun sotuv manageriga bonus.",
    )

    f_sm_fine_firstlesson_archived = models.IntegerField(
        default=0,
        help_text=(
            "Sinov darsi archivelanib ketganda, Sotuv manageriga jarima yoziladi. "
            "Sinov darsi o'quvchi sinov darsiga 3 martta kelmaganda Archivelanadi."
        ),
    )

    f_sm_fine_new_student_archived = models.IntegerField(
        default=0,
        help_text="Yangi o'quvchi aktivga o'tmasdan archivelanib ketsa, Sotuv manageriga jarima yoziladi.",
    )

    #######################################################
    ##     Service manageri uchun bonus va jarimalar     ##
    #######################################################

    f_svm_bonus_for_each_active_student = models.IntegerField(
        default=0,
        help_text="Har oyni 1 sanasida, soat 12:01 da oldingi oydagi barcha aktiv o'quvchilar uchun bonus.",
    )

    # TODO: Jarima qaysi etapdigi o'quvchilar uchun yozilishi kerak? Aktivmi? Yangimi? Hammasigami?
    f_svm_fine_student_archived = models.IntegerField(
        default=0, help_text="O'quvchi archivelanganda jarima yoziladi."
    )

    ###############################################################################################
    ##     Davomatchi, Filial bosh manageri, Monitorigchi, testolog uchun jarima va bonuslar     ##
    ###############################################################################################

    f_managers_bonus_for_each_active_student = models.IntegerField(
        default=0,
        help_text="Davomatchi, filial bosh manageri, monitoringchi, testolog uchun har oyni boshida, har bir aktiv o'quvchi uchun bonus.",
    )

    ###################################################
    ##     Head teacher uchun bonus va jarimalar     ##
    ###################################################

    f_ht_bonus_for_each_active_student = models.IntegerField(
        default=0,
        help_text="Har oyni boshida o'zi ishlidigan filiallar uchun har bitta aktiv o'quvchi uchu bonus.",
    )

    ##############################################
    ##     Teacher uchun bonus va jarimalar     ##
    ##############################################

    f_t_lesson_payment_percent = models.FloatField(
        default=0,
        help_text="Har darsda o'quvchilardan yechilgan dars pulidan qanchadur qismi, o'qituvchi hisobiga tushishi kerak. Foizlarda hisoblanadi.",
    )

    f_t_fine_failed_first_lesson = models.IntegerField(
        default=0,
        help_text="Sinov darsiga kelib, lekin aktivga o'tmasdan ketib qolsa, yoki boshqa o'qituvchiga o'tib ketib qolsa. Yoki boshqa filialga ketib qolsa. Jarima yoziladi.",
    )

    class Meta:
        abstract = True


class FinanceManagerKpi(BaseModel):

    employee: "Employee" = models.ForeignKey(
        "employee.Employee",
        on_delete=models.CASCADE,
        related_name="finance_manager_kpis",
    )

    action = models.CharField(
        max_length=255, choices=[("BONUS", "Bonus"), ("FINE", "Jarima")]
    )

    range = DecimalRangeField()

    amount = models.IntegerField()

    def clean(self):
        """Ensure valid numeric range and enforce min/max limits."""
        if not self.range:
            raise ValidationError("Range (range) is required.")

        lower, upper = self.range.lower, self.range.upper

        # must be defined
        if lower is None or upper is None:
            raise ValidationError("Both start and end values must be provided.")

        # order
        if lower >= upper:
            raise ValidationError("Start must be less than end.")

        # boundaries
        if lower < 0:
            raise ValidationError("Start cannot be less than 0.")
        if upper > 100:
            raise ValidationError("End cannot exceed 100.")

    class Meta(BaseModel.Meta):
        constraints = [
            *BaseModel.Meta.constraints,
            ExclusionConstraint(
                name="kpi_no_overlap_per_employee",
                expressions=[
                    ("employee", RangeOperators.EQUAL),
                    ("range", RangeOperators.OVERLAPS),
                ],
            ),
        ]

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)



