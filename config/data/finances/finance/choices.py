class FinanceKindTypeChoices:
    CASHIER_ACCEPTANCE = "CASHIER_ACCEPTANCE"
    CASHIER_HANDOVER = "CASHIER_HANDOVER"

    BONUS = "BONUS"
    SALARY = "SALARY"
    MONEY_BACK = "MONEY_BACK"
    LESSON_PAYMENT = "LESSON_PAYMENT"
    COURSE_PAYMENT = "COURSE_PAYMENT"
    VOUCHER = "VOUCHER"

    CHOICES = [
        (CASHIER_ACCEPTANCE, "Kassa qabul qilindi"),
        (CASHIER_HANDOVER, "Kassa topshirildi"),
        (BONUS, "Bonus"),
        (SALARY, "Maosh"),
        (MONEY_BACK, "Money Back"),
        (LESSON_PAYMENT, "Lesson Payment"),
        (COURSE_PAYMENT, "Course Payment"),
        (VOUCHER, "Vaucher"),
    ]
