from datetime import datetime, timedelta
from django.db.models import Avg
from .models import Room

def calculate_room_filling_statistics(room_id=None, start_time=str,end_time=str,
                                      lesson_duration=str):
    """
    Calculates student filling stats for a specific room (if given) or averages across all rooms.
    """
    if not start_time and end_time:
        start_time = datetime.strptime("08:00", "%H:%M")
        end_time = datetime.strptime("20:00", "%H:%M")
        lesson_duration = 2
    lessons_per_day = (end_time - start_time).seconds // (lesson_duration * 3600)  # 12 hours / 2 = 6 lessons

    if room_id:
        rooms = Room.objects.filter(id=room_id)
    else:
        rooms = Room.objects.all()

    room_statistics = []
    total_weekly_students = 0
    room_count = rooms.count()

    for room in rooms:
        room_filling = room.room_filling
        students_per_day = lessons_per_day * room_filling

        weekly_students = students_per_day * 6

        room_statistics.append({
            "room_id": room.id,
            "room_number": room.room_number,
            "room_filling": room_filling,
            "lessons_per_day": lessons_per_day,
            "students_per_day": students_per_day,
            "weekly_students": weekly_students,
        })

        total_weekly_students += weekly_students

    average_weekly_students = total_weekly_students / room_count if room_count > 0 else 0

    return {
        "individual_room_statistics": room_statistics,
        "average_weekly_students": round(average_weekly_students, 2),
    }
