from django.urls import path

from .views import AttendanceCreateAPIView, AttendanceGroupStateAPIView

from .views import AttendanceThemesAPIView, AttendanceStatusForDateAPIView


urlpatterns = [
    path("create", AttendanceCreateAPIView.as_view()),
    path("group/<uuid:group>/status", AttendanceGroupStateAPIView.as_view()),
    path("themes", AttendanceThemesAPIView.as_view()),
    path("status_for_date", AttendanceStatusForDateAPIView.as_view()),
]
