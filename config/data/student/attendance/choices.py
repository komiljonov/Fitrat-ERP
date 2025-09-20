class AttendanceStatusChoices:

    EMPTY = "EMPTY"

    IS_PRESENT = "IS_PRESENT"
    REASONED = "REASONED"
    UNREASONED = "UNREASONED"
    # HOLIDAY = "HOLIDAY"

    CHOICES = [
        (IS_PRESENT, "IS_PRESENT"),
        (REASONED, "Sababli"),
        (UNREASONED, "Sababsiz"),
        (EMPTY, "Belgilanmagan"),
        # (HOLIDAY, "Dam olish kuni"),
    ]
