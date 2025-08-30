from django.urls import include, path


urlpatterns = [path("attendances/", include("data.student.attendance.v2.urls"))]
