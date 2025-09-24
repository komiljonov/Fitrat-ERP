from typing import TYPE_CHECKING

from data.student.student.models import Student

if TYPE_CHECKING:
    from data.employee.models import Employee


class EmployeeMethods:

    def calculate_monthly_salary(self: "Employee"):

        if self.role == "SERVICE_MANAGER":

            if self.f_svm_bonus_for_each_active_student > 0:

                self.calculate_monthly_bonus_for_service_manager()

        if self.role == "FILIAL_Manager":

            print("Filial manager")

            if self.f_managers_bonus_for_each_active_student > 0:
                self.calculate_monthly_bonus_for_filial_manager()

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
