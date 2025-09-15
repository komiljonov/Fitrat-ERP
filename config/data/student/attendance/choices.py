class AttendanceStatusChoices:

    IS_PRESENT = "IS_PRESENT"
    REASONED = "REASONED"
    UNREASONED = "UNREASONED"
    HOLIDAY = "HOLIDAY"

    CHOICES = [
        (IS_PRESENT, "IS_PRESENT"),
        (REASONED, "Sababli"),
        (UNREASONED, "Sababsiz"),
        (HOLIDAY, "Dam olish kuni"),
    ]
