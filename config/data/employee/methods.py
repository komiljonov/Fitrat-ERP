from typing import TYPE_CHECKING
from django.db import transaction


from data.student.student.models import Student

if TYPE_CHECKING:
    from data.employee.models import Employee


class EmployeeMethods:

    def calculate_monthly_salary(self: "Employee"):

        if self.role == "SERVICE_MANAGER":

            if self.f_svm_bonus_for_each_active_student > 0:

                self.calculate_monthly_bonus_for_service_manager()

        if self.role in [
            "FILIAL_Manager",
            "MONITORING_MANAGER",
            "TESTOLOG",
            "HEAD_TEACHER",
        ]:

            if self.f_managers_bonus_for_each_active_student > 0:
                self.calculate_monthly_bonus_for_filial_manager()

        if self.role == "ACCOUNTING":

            if self.finance_manager_kpis.exists():

                self.calculate_kpi_for_entitled_students()

    def calculate_monthly_bonus_for_service_manager(self: "Employee"):

        if self.f_svm_bonus_for_each_active_student == 0:
            return

        active_students = Student.objects.filter(
            is_archived=False, student_stage_type="ACTIVE_STUDENT", service_manager=self
        )

        self.transactions.create(
            reason="BONUS_FOR_EACH_ACTIVE_STUDENT",
            amount=self.f_svm_bonus_for_each_active_student * active_students.count(),
            comment=f"Har bir aktiv o'quvchi uchun bonus. Bonus miqdori: f_managers_bonus_for_each_active_student{self.f_svm_bonus_for_each_active_student}, O'quvchilar soni: {active_students.count()}",
        )

    def calculate_monthly_bonus_for_filial_manager(self: "Employee"):

        if self.f_managers_bonus_for_each_active_student == 0:
            return

        active_students = Student.objects.filter(
            filial__in=self.filial.all(),
            is_archived=False,
            student_stage_type="ACTIVE_STUDENT",
        )

        print(f"Service manager o'quvchilari: {active_students}")

        self.transactions.create(
            reason="BONUS_FOR_EACH_ACTIVE_STUDENT",
            amount=self.f_managers_bonus_for_each_active_student
            * active_students.count(),
            comment=f"Har bir aktiv o'quvchi uchun bonus. Bonus miqdori: {self.f_managers_bonus_for_each_active_student}, O'quvchilar soni: {active_students.count()}",
        )

    def calculate_kpi_for_entitled_students(self: "Employee"):
        """
        Calculate entitled students percentage and apply KPI bonuses/fines.

        Returns:
            dict: Summary of actions taken
        """
        students = Student.objects.filter(is_archived=False)
        total = students.count()

        # Calculate percentage of students without debt
        if total > 0:
            non_debt = students.filter(balance__gte=0).count()
            entitled_students = round((non_debt / total) * 100, 2)
        else:
            entitled_students = 0

        # Find matching KPI rule
        kpi = self.finance_manager_kpis.filter(
            range__num_contains=entitled_students
        ).first()

        if not kpi:
            return

        with transaction.atomic():
            if kpi.action == "bonus":
                # Create bonus income transaction for each student
                for student in students:
                    self.transactions.create(
                        reason="BONUS_FOR_EACH_ENTITLED_STUDENT",
                        amount=kpi.amount,
                        comment=f"KPI Bonus: {entitled_students}% entitled students",
                        student=student,
                        # employee=self,
                        # student=student,
                        # transaction_type="income",
                        # amount=kpi.amount,
                        # description=f"KPI Bonus: {entitled_students}% entitled students",
                        # related_kpi=kpi,  # Optional: if you want to track which KPI triggered it
                    )
            elif kpi.action == "fine":
                # Create fine transaction for each student
                for student in students:
                    self.transactions.create(
                        reason="BONUSFINE_FOR_EACH_INDEBT_STUDENT_FOR_EACH_ENTITLED_STUDENT",
                        amount=kpi.amount,
                        comment=f"KPI Bonus: {entitled_students}% entitled students",
                        student=student,
                    )
