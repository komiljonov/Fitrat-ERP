
from datetime import datetime, timedelta

def calculate_lessons(start_date, end_date, lesson_type, holidays, days_off):
    """
    Calculate lesson schedule based on start and end dates, lesson type, holidays, and days off.

    Args:
        start_date (str): Start date of the group (YYYY-MM-DD).
        end_date (str): End date of the group (YYYY-MM-DD).
        lesson_type (str): Type of lesson ("ODD", "EVEN", "EVERYDAY").
        holidays (list): List of holidays (YYYY-MM-DD).
        days_off (list): List of day-off weekdays (e.g., ["Sunday"]).

    Returns:
        list: List of scheduled lesson dates (YYYY-MM-DD).
    """

    start_date = datetime.strptime(start_date, "%Y-%m-%d")
    end_date = datetime.strptime(end_date, "%Y-%m-%d")
    holidays = set(datetime.strptime(date, "%Y-%m-%d") for date in holidays)

    # Days off as numbers (Monday=0, Sunday=6)
    days_off_numbers = {["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"].index(day) for day in days_off}

    # Weekday mappings for ODD and EVEN lessons
    odd_days = {0, 2, 4}  # Monday, Wednesday, Friday
    even_days = {1, 3, 5}  # Tuesday, Thursday, Saturday

    # Generate all dates in the range
    all_dates = [start_date + timedelta(days=i) for i in range((end_date - start_date).days + 1)]

    # Filter dates based on lesson type
    if lesson_type == "ODD":
        lesson_days = [date for date in all_dates if date.weekday() in odd_days]
    elif lesson_type == "EVEN":
        lesson_days = [date for date in all_dates if date.weekday() in even_days]
    elif lesson_type == "EVERYDAY":
        lesson_days = [date for date in all_dates if date.weekday() not in {6}]  # Monday to Saturday (exclude Sunday)
    else:
        raise ValueError("Invalid lesson type. Must be 'ODD', 'EVEN', or 'EVERYDAY'.")

    # Filter out holidays and days off
    schedule = [
        date.strftime("%Y-%m-%d")
        for date in lesson_days
        if date not in holidays and date.weekday() not in days_off_numbers
    ]

    return schedule



# # Example usage
# start_date = "2025-01-01"
# end_date = "2025-01-31"
# lesson_type = "ODD"  # Can be "ODD", "EVEN", or "EVERYDAY"
# holidays = ["2025-01-10", "2025-01-15"]
# days_off = ["Saturday", "Sunday"]
#
# schedule = calculate_lessons(start_date, end_date, lesson_type, holidays, days_off)
# print(schedule)
