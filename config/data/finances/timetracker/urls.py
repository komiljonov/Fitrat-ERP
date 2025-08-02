from django.urls import  path

from .models import UserTimeLine
from .views import AttendanceList, UserTimeLineList, UserTimeLineDetail, TimeTrackerList, \
    TimeLineBulkCreate, AttendanceDetail, UserTimeLineBulkUpdateDelete, EmployeeAttendanceListView

urlpatterns = [
    path("", AttendanceList.as_view()),
    path("<uuid:pk>/", AttendanceDetail.as_view()),

    path("timeline/",UserTimeLineList.as_view()),
    path("timeline/<uuid:pk>",UserTimeLineDetail.as_view()),
    path("all/",TimeTrackerList.as_view()),

    path("timeline/bulk",TimeLineBulkCreate.as_view()),
    path("timeline/bulk/update",UserTimeLineBulkUpdateDelete.as_view()),

    path("all/fixed/",EmployeeAttendanceListView.as_view()),
]