from data.account.models import CustomUser
from data.finances.timetracker.models import UserTimeLine, Stuff_Attendance



def recalculate(check_in,check_out : None,employee_id):
    if check_in and check_out is None:
        date = check_in.date()

        staff_att = Stuff_Attendance.objects.filter(employee__id=employee_id,date=date).all()
        if staff_att:
            for att in staff_att.order_by("check_in"):
                pass



