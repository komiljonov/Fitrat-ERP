from django.urls import path

from .views import AttendanceCreateAPIView


urlpatterns = [path("", AttendanceCreateAPIView.as_view())]
