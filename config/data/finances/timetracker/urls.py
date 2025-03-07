from django.urls import  path

from .views import AttendanceList,AttendanceDetail

urlpatterns = [
    path("", AttendanceList.as_view()),
    path("<uuid:pk>/", AttendanceDetail.as_view()),
]