from collections import defaultdict
from datetime import timedelta, datetime

from dateutil.utils import today


def calculate_lessons(start_date, end_date:None, lesson_type, holidays, days_off):
    """
    Calculate lesson schedule based on start and end dates, lesson type (specific weekdays), holidays, and days off.

    Args:
        start_date (str): Start date of the group (YYYY-MM-DD).
        end_date (str, optional): End date of the group (YYYY-MM-DD). Defaults to today + 365 days.
        lesson_type (str): Comma-separated weekdays for the lesson schedule (e.g., "Monday,Wednesday,Friday").
        holidays (list): List of holidays (YYYY-MM-DD).
        days_off (list): List of day-off weekdays (e.g., ["Sunday"]).

    Returns:
        dict: Dictionary where the key is the month and the value is a list of scheduled lesson dates (YYYY-MM-DD).
    """
    # Parse start date
    start_date = datetime.strptime(str(start_date), "%Y-%m-%d")

    # Set default end date to today + 365 days if not provided
    if end_date is None:
        end_date = datetime.today() + timedelta(days=365)
    else:
        end_date = datetime.strptime(str(end_date), "%Y-%m-%d")


    holidays = set(datetime.strptime(date, "%Y-%m-%d") for date in holidays if date)

    days_off_numbers = {["Dushanba", "Seshanba", "Chorshanba", "Payshanba", "Juma", "Shanba", "Yakshanba"].index(day) for
                        day in days_off}

    lesson_days = [day.strip() for day in lesson_type.split(',')]

    lesson_day_numbers = {["Dushanba", "Seshanba", "Chorshanba", "Payshanba", "Juma", "Shanba", "Yakshanba"].index(day) for
                          day in lesson_days}

    all_dates = [start_date + timedelta(days=i) for i in range((end_date - start_date).days + 1)]


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