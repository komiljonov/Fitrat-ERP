# from datetime import time
# from .models import Lesson
#
# def is_schedule_conflict(room_number, day, start_time, end_time):
#     """
#     Check if there is a conflict for the given room, day, and time range.
#     """
#     conflicts = Lesson.objects.filter(
#         room_number=room_number,
#         day=day,
#         start_time__lt=end_time,  # Overlap: Starts before another lesson ends
#         end_time__gt=start_time,  # Overlap: Ends after another lesson starts
#     )
#     return conflicts.exists()
