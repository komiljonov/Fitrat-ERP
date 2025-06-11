from data.account.models import CustomUser
from data.finances.timetracker.models import UserTimeLine


# def recalculate(user,check_in,check_out:None):
#
#     date = check_in.date()
#
#     timeline = UserTimeLine.objects.filter(
#         user__id=user,
#         day=date.isoweekday(),
#     ).all()
#
#     user = CustomUser.objects.filter(user__id=user).first()
#
#     if user in ["TEACHER" , "ASSISTANT"] and (user.calculate_penalties or user.calculate_bonus):
#         if timeline:
#             for item in timeline:
#                 start_time = item.start_time
#                 end_time = item.end_time
#                 is_weekend = item.is_weekend
#                 penalty = item.penalty
#                 bonus = item.bonus
#
#                 if is_weekend:
#                     return {
#                         "bonus": 0,
#                         "penalty": 0,
#                     }
#
#                 if check_in and check_out is None:
#

