from typing import TYPE_CHECKING

from data.student.student.models import Student

if TYPE_CHECKING:
    from data.employee.models import Employee


class EmployeeMethods:

    def calculate_monthly_salary(self: "Employee"):

        if self.role == "SERVICE_MANAGER":

            print(f"Service manager: {self.full_name}")

            if self.f_svm_bonus_for_each_active_student > 0:

                self.calculate_monthly_salary_for_service_manager()

    def calculate_monthly_salary_for_service_manager(self: "Employee"):

        if self.f_svm_bonus_for_each_active_student == 0:
            return

        active_students = Student.objects.filter(
            is_archived=False, student_stage_type="ACTIVE_STUDENT", service_manager=self
        )

        print(f"Service manager o'quvchilari: {active_students}")

        self.transactions.create(
            reason="BONUS_FOR_EACH_ACTIVE_STUDENT",
            amount=self.f_svm_bonus_for_each_active_student * active_students.count(),
            comment=f"Har bir aktiv o'quvchi uchun bonus. Bonus miqdori: {self.f_svm_bonus_for_each_active_student}, O'quvchilar soni: {active_students.count()}",
        )
