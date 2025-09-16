from django.urls import path

from .views import AttendanceCreateAPIView, AttendanceGroupStateAPIView


urlpatterns = [
    path("create", AttendanceCreateAPIView.as_view()),
    path("group/<uuid:group>/status", AttendanceGroupStateAPIView.as_view()),
]
