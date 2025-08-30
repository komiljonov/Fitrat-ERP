from django.urls import path

from .views import AttendanceCreateAPIView


urlpatterns = [path("create", AttendanceCreateAPIView.as_view())]
