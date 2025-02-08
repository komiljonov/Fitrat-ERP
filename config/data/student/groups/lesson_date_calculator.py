from collections import defaultdict
from datetime import timedelta, datetime


def calculate_lessons(start_date, end_date, lesson_type, holidays, days_off):
    """
    Calculate lesson schedule based on start and end dates, lesson type (specific weekdays), holidays, and days off.

    Args:
        start_date (str): Start date of the group (YYYY-MM-DD).
        end_date (str): End date of the group (YYYY-MM-DD).
        lesson_type (str): Comma-separated weekdays for the lesson schedule (e.g., "Monday,Wednesday,Friday").
        holidays (list): List of holidays (YYYY-MM-DD).
        days_off (list): List of day-off weekdays (e.g., ["Sunday"]).

    Returns:
        dict: Dictionary where the key is the month and the value is a list of scheduled lesson dates (YYYY-MM-DD).
    """

    start_date = str(start_date)
    start_date = datetime.strptime(start_date, "%Y-%m-%d")
    end_date = datetime.strptime(end_date, "%Y-%m-%d")

    # Filter out empty strings from holidays list
    holidays = set(datetime.strptime(date, "%Y-%m-%d") for date in holidays if date)

    # Days off as numbers (Monday=0, Sunday=6)
    days_off_numbers = {["Dushanba", "Seshanba", "Chorshanba", "Payshanba", "Juma", "Shanba", "Yakshanba"].index(day) for
                        day in days_off}

    # Split the lesson_type into a list of days (e.g., "Monday,Wednesday,Friday" -> ["Monday", "Wednesday", "Friday"])
    lesson_days = [day.strip() for day in lesson_type.split(',')]

    # Weekday mappings for lesson days
    lesson_day_numbers = {["Dushanba", "Seshanba", "Chorshanba", "Payshanba", "Juma", "Shanba", "Yakshanba"].index(day) for
                          day in lesson_days}

    # Generate all dates in the range
    all_dates = [start_date + timedelta(days=i) for i in range((end_date - start_date).days + 1)]

    # Filter dates based on the lesson days (e.g., Monday, Wednesday, Friday)
    lesson_days_in_range = [date for date in all_dates if date.weekday() in lesson_day_numbers]

    # Filter out holidays and days off
    valid_dates = [
        date for date in lesson_days_in_range
        if date not in holidays and date.weekday() not in days_off_numbers
    ]

    # Group by month
    grouped_schedule = defaultdict(list)
    for date in valid_dates:
        grouped_schedule[date.strftime("%Y-%m")]  # Use Year-Month format as the key
        grouped_schedule[date.strftime("%Y-%m")].append(date.strftime("%Y-%m-%d"))

    return dict(grouped_schedule)